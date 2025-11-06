from rest_framework.serializers import ModelSerializer

from .models import Keys

class KeySerializer(ModelSerializer):
	class Meta:
		model = Keys
		fields = '__all__'