from .serializers import KeySerializer, UnlockAttemptSerializer, KeyLockPermissionSerializer
from .models import KeyLockPermissions
from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.db import connection
from django.utils import timezone

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


def create_key(key_data):
    key_serializer = KeySerializer(data=key_data)
    key_serializer.is_valid(raise_exception=True)
    return key_serializer.save()

def test_user_access(assigned_user, lock_id):
    print(assigned_user.pk, lock_id)
    return KeyLockPermissions.objects.filter(
            key__assigned_user=assigned_user.id,
            lock__lock_id=lock_id,
            key__is_revoked = False,
            key__not_valid_before__lte = timezone.now(),
        ).filter(
            Q(key__not_valid_after__isnull = True) | Q(key__not_valid_after__gte = timezone.now())
        ).exists()

def unlock_attempt(attempt_data):
    attempt_serializer = UnlockAttemptSerializer(data=attempt_data)
    attempt_serializer.is_valid(raise_exception=True)
    attempt_serializer.save()
    
    return Response(
        attempt_data,
        status=status.HTTP_200_OK,
    )

def validate_data(assigned_user, admin_user, start_date, end_date, lock_id):
    if not assigned_user:
        raise ValidationError(
            {
                "detail": "Assigned user not found!",
                "status": "Unsuccessful",
                "assigned_user":assigned_user.username
            }
        )

    if not admin_user.is_staff:
        raise ValidationError(
            {
                "detail": "Admin user not found!",
                "status": "Unsuccessful",
            }
        )

    if start_date > end_date:
        raise ValidationError(
            {
                "detail": "Start date is after end date?!?!",
                "status": "Unsuccessful",
            }
        )

    has_access = test_user_access(assigned_user, lock_id)

    print(has_access)

    if has_access:
        raise ValidationError(
            {
                "detail":"User already has a key with access to this lock.",
                "status":"Already reported"
            }
        )
