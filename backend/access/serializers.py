from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import Keys, UnlockAttempts, AuthUser, Locks, KeyLockPermissions
from django.db.models import BigAutoField


class KeyLockPermissionSerializer(ModelSerializer):
	class Meta:
		model = KeyLockPermissions
		fields = '__all__'

class UnlockAttemptSerializer(ModelSerializer):
	class Meta:
		model = UnlockAttempts
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
    lock_id = serializers.CharField()
    uid = serializers.CharField()

class UserMiniSerializer(ModelSerializer):
	class Meta:
		model = AuthUser
		fields = ['username']

class KeyMiniSerializer(ModelSerializer):
	assigned_user = UserMiniSerializer()

	class Meta:
		model = Keys
		fields = ['key_id','assigned_user',]

class LockMiniSerializer(ModelSerializer):
	class Meta:
		model = Locks
		fields = ['name','location','status']

class LockSerializer(ModelSerializer):
	class Meta:
		model = Locks
		fields = '__all__'

class UnlockAttemptMiniSerializer(ModelSerializer):
	lock = LockMiniSerializer()
	key = KeyMiniSerializer()
	user = UserMiniSerializer()

	class Meta:
		model = UnlockAttempts
		fields = ['user','lock','key','attempted_at','permission','result','reason']

class KeyGenerationSerializer(ModelSerializer):
	username = serializers.CharField()
	lock_id = serializers.IntegerField()
	class Meta: 
		model = Keys
		fields = ['username','not_valid_after','not_valid_before','key_name','lock_id']

class KeySerializer(ModelSerializer):
	created_at = serializers.DateTimeField(required=False)
	issued_ad = serializers.DateTimeField(required=False)

	class Meta:
		model = Keys 
		fields = '__all__'