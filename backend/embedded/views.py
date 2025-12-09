from django.shortcuts import render
from rest_framework.views import APIView
from .models import Keys, Locks, AuthUser, KeyLockPermissions, UnlockAttempts
from .serializers import LockIdSerializer, CardRequestSerializer, UnlockAttemptSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from datetime import datetime


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

        lock_id = serializer.validated_data['lock_id']
        auth_user = AuthUser.objects.get(username=request.user.username)

        # Check if this user has ANY key that can open this lock
        has_access = KeyLockPermissions.objects.filter(
            key__assigned_user=auth_user,
            lock__lock_id=lock_id
        ).exists()

        try:
            lock = Locks.objects.get(lock_id=lock_id)
        except Locks.DoesNotExist:
            # No such key → no access
            return Response(
                {
                    "lock_id": lock_id,
                    "has_access": False,
                    "reason": "Invalid Lock ID",
                },
                status=status.HTTP_200_OK,
            )


        lock_status = lock.status

        if(has_access):
            lock_status = not lock_status

        lock.status = lock_status
        lock.save()

        perm_row = (
            KeyLockPermissions.objects
            .filter(
                key__assigned_user=auth_user,
                lock__lock_id=lock_id,
            )
            .order_by('key_id')
            .values('key_id')
            .first()
        )        
        key = Keys.objects.get(pk=perm_row['key_id']) if perm_row else None

        attempt_data = {
            "result": "granted" if has_access else "denied",
            "attempted_at": datetime.now(),
            "user": auth_user.id,        # FK → pass the ID
            "lock": lock.lock_id,        # or lock.id, depending on your model
            "key": key.key_id if key else None,
        }

        attempt_serializer = UnlockAttemptSerializer(data=attempt_data)
        attempt_serializer.is_valid(raise_exception=True)
        attempt_serializer.save()

        return Response(
            {
                "lock_id": lock_id,
                "user_id": auth_user.id,
                "lock_status": lock_status,
            },
            status=status.HTTP_200_OK,
        )

class CardLockAccessView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CardRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lock_id = serializer.validated_data['lock_id']
        uid = serializer.validated_data['uid']

        try:
            key = Keys.objects.get(credential=uid)
        except Keys.DoesNotExist:
            # No such key → no access
            return Response(
                {
                    "lock_id": lock_id,
                    "has_access": False,
                    "reason": "Invalid code",
                },
                status=status.HTTP_200_OK,
            )

        try:
            lock = Locks.objects.get(lock_id=lock_id)
        except Locks.DoesNotExist:
            # No such key → no access
            return Response(
                {
                    "lock_id": lock_id,
                    "has_access": False,
                    "reason": "Invalid Lock ID",
                },
                status=status.HTTP_200_OK,
            )

        # Check if this user has ANY key that can open this lock
        has_access = KeyLockPermissions.objects.filter(
            key__credential=uid,
            lock__lock_id=lock_id
        ).exists()

        lock_status = lock.status

        attempt_data = {
            "result": "granted" if has_access else "denied",
            "attempted_at": datetime.now(),
            "user": 39,        # FK → pass the ID
            "lock": lock.lock_id,        # or lock.id, depending on your model
            "key": key.key_id if key else None,
        }

        attempt_serializer = UnlockAttemptSerializer(data=attempt_data)
        attempt_serializer.is_valid(raise_exception=True)
        attempt_serializer.save()


        if(has_access):
            lock_status = not lock_status

        lock.status = lock_status
        lock.save()

        return Response(
            {
                "lock_id": lock_id,
                "lock_status": lock_status,
            },
            status=status.HTTP_200_OK,
        )

