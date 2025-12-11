from rest_framework.serializers import ModelSerializer 
from rest_framework import serializers
from .models import Keys, UnlockAttempts, AuthUser, Locks

class KeySerializer(ModelSerializer):
	class Meta:
		model = Keys
		fields = '__all__'

class UnlockAttemptSerializer(ModelSerializer):
	class Meta:
		model = UnlockAttempts
		fields = '__all__'


class LockIdSerializer(serializers.Serializer):
    lock_id = serializers.CharField()

class CardRequestSerializer(serializers.Serializer):
    lock_id = serializers.CharField()
    uid = serializers.CharField()

class UserMiniSerializer():
	class Meta:
		model = AuthUser
		fields = ['username']

class KeyMiniSerializer(serializers.Serializer):
	assigned_user = UserMiniSerializer()

	class Meta:
		model = Keys
		fields = ['key_id','assigned_user',]

class LockMiniSerializer(serializers.Serializer):
	class Meta:
		model = Locks
		fields = ['name','location','status']

class UnlockAttemptMiniSerializer(serializers.Serializer):
	lock = LockMiniSerializer()
	key = KeyMiniSerializer()
	user = UserMiniSerializer()

	class Meta:
		model = UnlockAttempts
		fields = ['user','lock','key','attempted_at','permission','result','reason']