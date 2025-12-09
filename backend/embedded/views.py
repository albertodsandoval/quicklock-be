from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.views import APIView
from .models import Keys, Locks, AuthUser, KeyLockPermissions
from .serializers import KeySerializer
from .serializers import LockIdSerializer, CardRequestSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
import json


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

        print(lock_status)

        if(has_access):
            lock_status = not lock_status

        lock.status = lock_status
        lock.save()


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

