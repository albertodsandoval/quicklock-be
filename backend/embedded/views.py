from django.shortcuts import render
from rest_framework.views import APIView
from .models import Keys, Locks, AuthUser, KeyLockPermissions, UnlockAttempts
from .serializers import LockIdSerializer, CardRequestSerializer, UnlockAttemptMiniSerializer, KeyGenerationSerializer, KeySerializer, RequestStatusResponseSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.core import serializers
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from .utils import create_key, test_user_access, unlock_attempt, validate_data, create_key_lock_permission



# class RequestStatusView(APIView):
#     permission_classes = [permissions.AllowAny]

#     @extend_schema(
#         summary="Checks status of a lock",
#         request=LockIdSerializer,
#         responses=RequestStatusResponseSerializer
#     )
#     def post(self, request):
#         serializer = LockIdSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)


#         lock_id = serializer.validated_data['lock_id']

#         try:
#             lock = Locks.objects.get(lock_id=lock_id)
#             response_data = {
#                 "lock_id": lock_id,
#                 "request_status": True,
#                 "lock_status": lock.status,
#             }
#         except Locks.DoesNotExist:
#             return Response(
#                 {"detail": "Invalid Lock ID"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         response_serializer = RequestStatusResponseSerializer(response_data)

#         return Response(
#                 {
#                     "lock_id": lock_id,
#                     "request_status": True,
#                     "lock_status": lock.status
#                 },
#                 status=status.HTTP_200_OK,
#             )

class RequestStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Checks status of a lock",
        request=LockIdSerializer,
        responses={
            200: RequestStatusResponseSerializer,
            404: OpenApiResponse(description="Invalid Lock ID"),
        },
    )
    def post(self, request):
        req_serializer = LockIdSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        lock_id = req_serializer.validated_data["lock_id"]

        lock = get_object_or_404(Locks, lock_id=lock_id)

        response_data = {
            "lock_id": lock_id,
            "request_status": True,
            "lock_status": lock.status,
        }
        res_serializer = RequestStatusResponseSerializer(response_data)

        return Response(res_serializer.data, status=status.HTTP_200_OK)

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
                "attempted_at":timezone.now()
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
                "attempted_at":timezone.now()
            }

            return unlock_attempt(attempt_data)

        now = timezone.now()

        # Check if this user has a key that can open this lock
        has_access = test_user_access(auth_user, lock_id)

        # if user has key but not a valid one
        if (not has_access):
            attempt_data = {
                "permission": "denied",
                "user": auth_user.id,
                "lock": lock_id,        # or lock.id, depending on your model
                "reason": "User has no valid key for this lock.",
                "result": lock.status,
                "attempted_at":timezone.now()
            }

            return unlock_attempt(attempt_data)

        lock_status = not lock.status

        lock.status = lock_status
        lock.save()

        key_id_row = (
            KeyLockPermissions.objects
            .filter(
                key__assigned_user=auth_user,
                lock_id=lock_id,  # FK column, safest
                key__is_revoked=False,
                key__not_valid_before__lte=now,
            )
            .filter(Q(key__not_valid_after__isnull=True) | Q(key__not_valid_after__gte=now))
            .order_by("-key__not_valid_before", "-key_id")   # pick “most recent” valid key
            .values("key_id")
            .first()
        )

        key_id = key_id_row["key_id"]


        attempt_data = {
            "permission": "granted",
            "user": auth_user.id,
            "lock": lock_id,
            "key": key_id,
            "result": lock.status,
            "attempted_at":timezone.now()
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
                "attempted_at":timezone.now(),
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
                "attempted_at":timezone.now(),
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
                "attempted_at": timezone.now(),
                "user": auth_user.id,        # FK → pass the ID
                "lock": lock_id,        # or lock.id, depending on your model
                "key": key.key_id if key else None,
                "result": lock.status,
                "presented_credential": uid,
            }

            return unlock_attempt(attempt_data)

        attempt_data = {
            "permission": "denied",
            "attempted_at": timezone.now(),
            "user": auth_user.id,        # FK → pass the ID
            "lock": lock_id,        # or lock.id, depending on your model
            "key": key.key_id if key else None,
            "result": lock.status,
            "presented_credential": uid,
            "reason": "This user does not possess a key with permission to this lock."
        }

        return unlock_attempt(attempt_data)


class LogsByUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UnlockAttemptMiniSerializer

    def get(self, request):
        user = request.user

        logs = UnlockAttempts.objects.filter(
            user__username=user
        ).order_by('-attempted_at')

        return Response(
            UnlockAttemptMiniSerializer(logs, many=True).data,
            status=status.HTTP_200_OK,
        )


class GenerateKeyView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):

        serializer = KeyGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # users involved
        admin_user = request.user
        assigned_user = AuthUser.objects.filter(username=serializer.validated_data['username']).first()

        # conditions
        end_date = serializer.validated_data["not_valid_after"]
        start_date = serializer.validated_data["not_valid_before"]
        key_name = serializer.validated_data["key_name"]
        lock_id = serializer.validated_data["lock_id"]

        response = validate_data(assigned_user, admin_user, start_date, end_date, lock_id)

        if response:
            return response
        key_data = {
            "assigned_user":assigned_user.id,
            "administrator":admin_user.id,
            "key_name":key_name,
            "not_valid_after":end_date,
            "not_valid_before":start_date,
            "is_revoked": False,
        }

        key = create_key(key_data)

        print(key)

        key_lock_permission_data = {
            "key": key.key_id,
            "lock": lock_id,
            "created_at": timezone.now(),
            "created_by_administrator": admin_user.id
        }

        key_lock_permission = create_key_lock_permission(
            key_id=key.key_id,
            lock_id=lock_id,
            admin_user=admin_user
        )

        return Response(
            key_lock_permission,
            status=status.HTTP_201_CREATED
        )