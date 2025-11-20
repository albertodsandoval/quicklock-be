from rest_framework.serializers import ModelSerializer

from .models import AuthUser

class UserSerializer(ModelSerializer):
	class Meta:
		model = AuthUser
		fields = '__all__'