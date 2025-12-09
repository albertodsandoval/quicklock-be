from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Keys

class KeySerializer(ModelSerializer):
	class Meta:
		model = Keys
		fields = '__all__'


class LockIdSerializer(serializers.Serializer):
    lock_id = serializers.CharField()

class CardRequestSerializer(serializers.Serializer):
    lock_id = serializers.CharField()
    uid = serializers.CharField()