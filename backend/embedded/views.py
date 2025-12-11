from django.shortcuts import render
from rest_framework.views import APIView
from .models import Keys, Locks, AuthUser, KeyLockPermissions, UnlockAttempts
from .serializers import LockIdSerializer, CardRequestSerializer, UnlockAttemptSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from datetime import datetime
from django.db.models import Q


class RequestStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LockIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        lock_id = serializer.validated_data['lock_id']

        try:
            lock = Locks.objects.get(lock_id=lock_id)
        except Locks.DoesNotExist:
            return Response(
                {
                    "lock_id": lock_id,
                    "request_status": False,
                    "reason": "Invalid Lock ID",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
                {
                    "lock_id": lock_id,
                    "request_status": True,
                    "lock_status": lock.status
                },
                status=status.HTTP_200_OK,
            )

class MobileLockAccessView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # requires JWT-authenticated user

    def post(self, request):
        serializer = LockIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_user = AuthUser.objects.get(username=request.user.username)

        lock_id = serializer.validated_data['lock_id']

        try:
            lock = Locks.objects.get(lock_id=lock_id)
        except Locks.DoesNotExist:
            attempt_data = {
                "permission": "denied",
                "user": auth_user.id,       
                "lock": lock_id,     
                "reason": "Lock does not exist",
                "attempted_at":datetime.now()
            }
            # lock means no access
            return unlock_attempt(attempt_data)

        lock_status = lock.status


        user_has_key = Keys.objects.filter(assigned_user=auth_user)

        # if user has no key
        if (not user_has_key):
            attempt_data = {
                "permission": "denied",
                "user": auth_user.id,       
                "lock": lock_id,     
                "reason": "User has no keys.",
                "result": lock.status,
                "attempted_at":datetime.now()
            }

            return unlock_attempt(attempt_data)

        now = datetime.now()

        # Check if this user has a key that can open this lock
        has_access = KeyLockPermissions.objects.filter(
            key__assigned_user=auth_user,
            lock__lock_id=lock_id,
            key__is_revoked = False,
            key__not_valid_before__lte = now,
        ).filter(
            Q(key__not_valid_after__isnull = True) | Q(key__not_valid_after__gte = now)
        ).exists()

        # if user has key but not a valid one
        if (not has_access):
            attempt_data = {
                "permission": "denied",
                "user": auth_user.id,
                "lock": lock_id,        # or lock.id, depending on your model
                "reason": "User has no valid key for this lock.",
                "result": lock.status,
                "attempted_at":datetime.now()
            }

            return unlock_attempt(attempt_data)

        lock_status = not lock.status

        lock.status = lock_status
        lock.save()

        keylockperm = (
            KeyLockPermissions.objects
            .filter(
                key__assigned_user=auth_user,
                lock__lock_id=lock_id,
            )
            .order_by('key_id')
            .values('key_id')
            .first()
        )

        key = Keys.objects.get(key_id=keylockperm['key_id'])


        attempt_data = {
            "permission": "granted",
            "user": auth_user.id,
            "lock": lock_id,
            "key": key.key_id,
            "result": lock.status,
            "attempted_at":datetime.now()
        }

        return unlock_attempt(attempt_data)


class CardLockAccessView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CardRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lock_id = serializer.validated_data['lock_id']
        uid = serializer.validated_data['uid']


        try:
            lock = Locks.objects.get(lock_id=lock_id)
        except Locks.DoesNotExist:
            attempt_data = {
                "permission": "denied",
                "lock": lock_id,
                "reason": "Lock does not exist",
                "attempted_at":datetime.now(),
                "presented_credential": uid
            }

            # no lock means no access
            return unlock_attempt(attempt_data)

        lock_status = lock.status

        try:
            key = Keys.objects.get(credential=uid)
        except Keys.DoesNotExist:
            attempt_data = {
                "permission": "denied",
                "lock": lock_id,
                "reason": "Key does not exist",
                "result": lock_status,
                "attempted_at":datetime.now(),
                "presented_credential": uid
            }

            # no key means no access
            return unlock_attempt(attempt_data)

        auth_user = key.assigned_user

        # check if this uid has a key that can open this lock
        has_access = KeyLockPermissions.objects.filter(
            key__assigned_user=auth_user,
            lock__lock_id=lock_id
        ).exists()

        if(has_access):
            lock.status = not lock_status
            lock.save()

            attempt_data = {
                "permission": "granted",
                "attempted_at": datetime.now(),
                "user": auth_user.id,        # FK → pass the ID
                "lock": lock_id,        # or lock.id, depending on your model
                "key": key.key_id if key else None,
                "result": lock.status,
                "presented_credential": uid,
            }

            return unlock_attempt(attempt_data)

        attempt_data = {
            "permission": "denied",
            "attempted_at": datetime.now(),
            "user": auth_user.id,        # FK → pass the ID
            "lock": lock_id,        # or lock.id, depending on your model
            "key": key.key_id if key else None,
            "result": lock.status,
            "presented_credential": uid,
            "reason": "This user does not possess a key with permission to this lock."
        }
        return unlock_attempt(attempt_data)


def unlock_attempt(attempt_data):
    attempt_serializer = UnlockAttemptSerializer(data=attempt_data)
    attempt_serializer.is_valid(raise_exception=True)
    attempt_serializer.save()
    
    return Response(
        attempt_data,
        status=status.HTTP_200_OK,
    )
