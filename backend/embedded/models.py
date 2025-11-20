from django.db import models

# Create your models here.
class Keys(models.Model):
    key_id = models.BigAutoField(primary_key=True)
    assigned_user = models.ForeignKey('Users', models.DO_NOTHING, db_column='assigned_user')
    administrator = models.ForeignKey('Users', models.DO_NOTHING, related_name='keys_administrator_set')
    credential = models.TextField(unique=True, blank=True, null=True)
    key_name = models.TextField(blank=True, null=True)
    issued_ad = models.DateTimeField()
    not_valid_after = models.DateTimeField(blank=True, null=True)
    is_revoked = models.BooleanField()
    created_at = models.DateTimeField()
    not_valid_before = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'keys'

    def __str__(self):
    	return self.key_id


class Locks(models.Model):
    lock_id = models.BigAutoField(primary_key=True)
    administrator = models.ForeignKey('Users', models.DO_NOTHING)
    name = models.TextField()
    location = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'locks'


class UnlockAttempts(models.Model):
    attempt_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    lock = models.ForeignKey(Locks, models.DO_NOTHING)
    key = models.ForeignKey(Keys, models.DO_NOTHING)
    presented_credential = models.TextField(blank=True, null=True)
    result = models.TextField()  # This field type is a guess.
    reason = models.TextField(blank=True, null=True)
    attempted_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'unlock_attempts'

class Users(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    email = models.TextField(unique=True)  # This field type is a guess.
    username = models.TextField(unique=True)  # This field type is a guess.
    password_hash = models.TextField()
    first_name = models.TextField()
    last_name = models.TextField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    role = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'users'