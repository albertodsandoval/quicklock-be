from django.db import transaction
from abc import ABC, abstractmethod
from .models import AuthUser, KeyLockPermissions, UnlockAttempts, Keys, Locks
from datetime import datetime
from django.db.models import Q


@transaction.atomic
def mobile_toggle_lock(*, user, lock_id) -> dict:
    # heavy logic here
    return {"lock_id": lock_id, "status": True, "reason": None}

class BaseUnlockStrategy(ABC):
    def __init__(self, lock_id):
        self.lock_id = lock_id

    @abstractmethod
    def resolve_actor(self):
        """"""

    @transaction.atomic
    def execute(self):
        actor = self.resolve_actor()
        return self._toggle_and_log(actor)

    def _toggle_and_log(self, actor):
        now = datetime.now()

        lock = Locks.objects.get(lock_id=self.lock_id)
        if not lock:
            return create_lock_access_attempt(
                user=actor,
                lock=lock,
                key=key if key else None,
                presented_credential= None,
                attempted_at=now,
                permission='denied',
                result=lock.status,
                reason="Lock does not exist"
            )
        
        key = (
            Keys.objects
            .filter(
                assigned_user_id=actor,
                is_revoked=False,
                not_valid_before__lte=now,
            )
            .filter(
                Q(not_valid_after__isnull=True) |
                Q(not_valid_after__gte=now)
            )
            .filter(
                keylockpermissions__lock_id=self.lock_id
            )
            .order_by("-not_valid_before", "-key_id")
            .first()
        )
        if not key:
            return create_lock_access_attempt(
                user=actor,
                lock=lock,
                key=None,
                presented_credential=None,
                attempted_at=now,
                permission='denied', 
                result=lock.status,
                reason="User does not have a valid key for this lock."
            )


        lock.status = not lock.status
        lock.save()

        return create_lock_access_attempt(
            user=actor,
            lock=lock,
            key=key if key else None,
            presented_credential= None,
            attempted_at=now,
            permission='granted',
            result=lock.status,
            reason=None
        )
class MobileUnlockStrategy(BaseUnlockStrategy):
    def __init__(self, user, lock_id):
        super().__init__(lock_id)
        self.user = user

    def resolve_actor(self):
        user = AuthUser.objects.get(username=self.user.username)
        return user

class CardUnlockStrategy(BaseUnlockStrategy):
    def __init__(self, uid, lock_id):
        super().__init__(lock_id)
        self.uid = uid

    def resolve_actor(self):
        user = AuthUser.objects.get(keys_credential=uid)
        return user

def create_lock_access_attempt(
    *,
    user,
    lock,
    key,
    presented_credential,
    attempted_at,
    permission,
    result,
    reason
):
    unlock_attempt = UnlockAttempts(
        user=user,
        lock=lock,
        key=key,
        presented_credential=presented_credential,
        attempted_at=attempted_at,
        permission=permission,
        result=result
    )
    unlock_attempt.save()

    return unlock_attempt