# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class KeyLockPermissions(models.Model):
    key = models.ForeignKey('Keys', models.DO_NOTHING)
    lock = models.ForeignKey('Locks', models.DO_NOTHING)
    created_at = models.DateTimeField()
    created_by_administrator = models.ForeignKey('AuthUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'key_lock_permissions'


class Keys(models.Model):
    key_id = models.BigAutoField(primary_key=True)
    assigned_user = models.ForeignKey('AuthUser', models.DO_NOTHING, db_column='assigned_user')
    administrator = models.ForeignKey('AuthUser', models.DO_NOTHING, related_name='keys_administrator_set')
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


class Locks(models.Model):
    lock_id = models.BigAutoField(primary_key=True)
    administrator = models.ForeignKey('AuthUser', models.DO_NOTHING)
    name = models.TextField()
    location = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    status = models.BooleanField()
    class Meta:
        managed = False
        db_table = 'locks'


class UnlockAttempts(models.Model):
    attempt_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    lock = models.ForeignKey(Locks, models.DO_NOTHING)
    key = models.ForeignKey(Keys, models.DO_NOTHING)
    presented_credential = models.TextField(blank=True, null=True)
    result = models.TextField()  # This field type is a guess.
    reason = models.TextField(blank=True, null=True)
    attempted_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'unlock_attempts'
