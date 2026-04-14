from django.db import models
from django.db.models import Q
from django.utils import timezone


class KeyQuerySet(models.QuerySet):
    def valid(self, at=None):
        if at is None:
            at = timezone.now()

        return self.filter(
            is_revoked=False,
            not_valid_before__lte=at,
        ).filter(
            Q(not_valid_after__isnull=True) |
            Q(not_valid_after__gt=at)
        )