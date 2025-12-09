from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import AuthUser

class UserSerializer(ModelSerializer):
	class Meta:
		model = AuthUser
		fields = '__all__'

class RegistrationSerializer(serializers.Serializer):
	username = serializers.CharField()
	email = serializers.CharField()
	password = serializers.CharField()

class SendEmailSerializer(serializers.Serializer):
	username = serializers.CharField()
	email = serializers.CharField()
	password = serializers.CharField()

