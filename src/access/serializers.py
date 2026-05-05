from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import Keys, UnlockAttempts, AuthUser, Locks, KeyLockPermissions
from django.db.models import BigAutoField
from django.db import connection
from django.utils import timezone
from django.db.models import Q


class KeyLockPermissionSerializer(ModelSerializer):
    class Meta:
        model = KeyLockPermissions
        fields = '__all__'


class UnlockAttemptSerializer(ModelSerializer):
    location = serializers.CharField(source='lock.location', read_only=True)

    class Meta:
        model = UnlockAttempts
        fields = '__all__'


class KeySerializer(ModelSerializer):
    created_at = serializers.DateTimeField(required=False)

    class Meta:
        model = Keys
        fields = '__all__'


class LockIdSerializer(Serializer):
    lock_id = serializers.CharField()


class LockStatusSerializer(Serializer):
    lock_id = serializers.IntegerField()
    status = serializers.BooleanField()


class RequestStatusResponseSerializer(Serializer):
    lock_id = serializers.IntegerField()
    request_status = serializers.BooleanField()
    lock_status = serializers.BooleanField(required=False)
    reason = serializers.CharField(required=False)


class CardRequestSerializer(Serializer):
    uid = serializers.CharField()


class UserMiniSerializer(ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username']


class KeyMiniSerializer(ModelSerializer):
    assigned_user = UserMiniSerializer()

    class Meta:
        model = Keys
        fields = ['key_id', 'assigned_user',]


class LockMiniSerializer(ModelSerializer):
    class Meta:
        model = Locks
        fields = ['name', 'location', 'status']


class LockSerializer(ModelSerializer):
    is_staff = serializers.SerializerMethodField()

    class Meta:
        model = Locks
        fields = '__all__'

    def get_is_staff(self, obj):
        user = self.context['request'].user
        return user.is_staff


class KeyGenerationSerializer(ModelSerializer):
    user_email = serializers.EmailField(write_only=True)
    lock_id = serializers.IntegerField(write_only=True)
    administrator = serializers.CharField(write_only=True)

    class Meta:
        model = Keys
        fields = ['key_id', 'user_email', 'not_valid_after',
                  'not_valid_before', 'key_name', 'lock_id', 'credential',
                  'is_revoked', 'created_at', 'administrator']
        read_only_fields = ['key_id', 'created_at']
        extra_kwargs = {
            'not_valid_after': {'required': False},
            'not_valid_before': {'required': False},
            'administrator': {'required': False},
            'is_revoked': {'required': False}
        }

    def validate(self, data):
        if data['not_valid_after'] is not None:
            if data['not_valid_after'] < data['not_valid_before']:
                raise serializers.ValidationError(
                    "Start date is after end date.")

        has_access = KeyLockPermissions.objects.filter(
            key__assigned_user=data["user_email"],
            lock__lock_id=data["lock_id"].pk,
            key__is_revoked=False,
            key__not_valid_before__lte=timezone.now(),
        ).filter(
            Q(key__not_valid_after__isnull=True) | Q(
                key__not_valid_after__gte=timezone.now())
        ).exists()

        if has_access:
            raise serializers.ValidationError(
                """User already has access to this lock.
                Update their key instead.""")

        return data

    def validate_user_email(self, email):
        try:
            return AuthUser.objects.get(email=email)
        except AuthUser.DoesNotExist:
            raise serializers.ValidationError("No user with that email.")
        except AuthUser.MultipleObjectsReturned:
            raise serializers.ValidationError("Email not unique.")

    def validate_lock_id(self, lock_id):
        try:
            return Locks.objects.get(pk=lock_id)
        except Locks.DoesNotExist:
            raise serializers.ValidationError("No lock with that id.")

    def validate_administrator(self, administrator):
        try:
            administrator = AuthUser.objects.get(pk=administrator)
            if not administrator.is_staff:
                raise ValidationError(
                    "Signed in user is not an administrator.")
            return administrator
        except AuthUser.DoesNotExist:
            raise serializers.ValidationError("No user with that email.")
        except AuthUser.MultipleObjectsReturned:
            raise serializers.ValidationError("Email not unique.")

    def create(self, validated_data):
        user = validated_data.pop("user_email")
        lock_id = validated_data.pop("lock_id")
        administrator = validated_data.get("administrator")

        key = Keys.objects.create(assigned_user=user, **validated_data)

        create_key_lock_permission(
            key_id=key.pk,
            lock_id=lock_id.pk,
            admin_user=administrator
        )

        return key


def create_key_lock_permission(
    *,
    key_id: int,
    lock_id: int,
    admin_user,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO key_lock_permissions
                (key_id, lock_id, created_at, created_by_administrator_id)
            VALUES
                (%s, %s, %s, %s)
            """,
            [
                key_id,
                lock_id,
                timezone.now(),
                admin_user.pk,
            ],
        )

        return {
            "key_id": key_id,
            "lock_id": lock_id,
            "admin_user": admin_user.username
        }
