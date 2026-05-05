from .models import Keys, Locks, AuthUser, UnlockAttempts
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, permissions, viewsets
from django.core import serializers
from django.db.models import Q, F, OuterRef, Subquery, Exists
from .services import MobileUnlockStrategy, CardUnlockStrategy
from drf_yasg.utils import swagger_auto_schema, no_body
from django.utils import timezone

# ---------- LOCK VIEW SET --------------


class LockViewSet(viewsets.ModelViewSet):
    serializer_class = LockSerializer
    queryset = Locks.objects.all()
    lookup_field = "lock_id"

    @swagger_auto_schema(
        request_body=no_body,
        responses={200: LockStatusSerializer},
        security=[],
    )
    @action(detail=True, methods=['get'], permission_classes=[])
    def status(self, request, lock_id=None):
        """
        Retrieves status of the lock specified via path parameter
        'lock_id'.
        """
        lock = self.get_object()
        lock_status = LockStatusSerializer({
            "lock_id": lock.lock_id,
            "status": lock.status
        })
        return Response(lock_status.data)

    @swagger_auto_schema(
        request_body=no_body,
        responses={200: UnlockAttemptSerializer},
        security=[{"Bearer": []}],
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def mobile_unlock(self, request, lock_id=None):
        """
        Initiates an attempt to unlock a lock specified via path parameter
        'lock_id'. User must be logged in. Returns attempt information.
        """
        lock = self.get_object()
        service = MobileUnlockStrategy(user=request.user, lock_id=lock.lock_id)
        unlock_attempt = service.execute()

        return Response(UnlockAttemptSerializer(unlock_attempt).data)

    @swagger_auto_schema(
        request_body=CardRequestSerializer,
        responses={200: UnlockAttemptSerializer},
        security=[{"Bearer": []}],
    )
    @action(detail=True, methods=['post'], permission_classes=[])
    def card_unlock(self, request, lock_id=None):
        """
        Initiates an attempt to unlock a lock specified via path parameter
        'lock_id'. NFC card UID must be provided. Returns attempt information.
        """
        lock = self.get_object()
        service = CardUnlockStrategy(
            uid=request.data.get('uid'), lock_id=lock.lock_id)
        unlock_attempt = service.execute()

        return Response(UnlockAttemptSerializer(unlock_attempt).data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def list_by_user_access(self, request):
        """
        Returns all locks a user has access to determined by the
        keys associated with their account.
        """
        now = timezone.now()
        queryset = self.filter_queryset(Locks.objects.filter(
            keylockpermissions__key__assigned_user=request.user.pk,
            keylockpermissions__key__is_revoked=False,
            keylockpermissions__key__not_valid_before__lte=now,
        ).filter(
            Q(keylockpermissions__key__not_valid_after__isnull=True) |
            Q(keylockpermissions__key__not_valid_after__gt=now)
        ).distinct())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


# ---------- KEY VIEW SETS -------------
class KeyViewSet(viewsets.ModelViewSet):
    serializer_class = KeySerializer
    queryset = Keys.objects.all()

    @swagger_auto_schema(
        request_body=KeyGenerationSerializer,
        responses={200: KeyGenerationSerializer},
        security=[{"Bearer": []}],
    )
    def create(self, request, *args, **kwargs):
        """
        Creates a key for a user specified via their email.
        Leave not_valid_after empty to make key indefinite.
        Ignore credential for now.
        is_revoked defaults to false, it is not required.
        key_name is not required as well.
        """
        request.data['administrator'] = request.user.pk
        serializer = KeyGenerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


# ---------- LOGS VIEW SET --------------
class LogsViewSet(viewsets.ModelViewSet):
    serializer_class = UnlockAttemptSerializer
    queryset = UnlockAttempts.objects.all()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def read_by_user(self, request):
        """
        Returns all access attempts (logs) made by logged in user.
        """

        now = timezone.now()

        current_access = KeyLockPermissions.objects.filter(
            lock_id=OuterRef('lock_id'),
            key__assigned_user=request.user.pk,
            key__is_revoked=False,
            key__not_valid_before__lte=now,
        ).filter(
            Q(key__not_valid_after__isnull=True) |
            Q(key__not_valid_after__gt=now)
        )

        access_at_attempt = KeyLockPermissions.objects.filter(
            lock_id=OuterRef('lock_id'),
            key__assigned_user=request.user.pk,
            created_at__lte=OuterRef('attempted_at'),
        )

        queryset = self.filter_queryset(
            UnlockAttempts.objects.select_related('lock', 'user', 'key')
            .annotate(
                has_current_access=Exists(current_access),
                had_access_before_attempt=Exists(access_at_attempt),
            )
            .filter(
                has_current_access=True,
                had_access_before_attempt=True,
            )
            .order_by('-attempted_at')
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAdminUser]
    )
    def read_by_admin(self, request):
        """
        Returns all access attempts (logs) made on locks owned by the logged
        in administrator. Must be administrator to access this endpoint.
        """
        queryset = self.filter_queryset(UnlockAttempts.objects.filter(
            lock__administrator_id=request.user.pk
        ))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
