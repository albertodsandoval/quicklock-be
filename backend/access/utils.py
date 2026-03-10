from .serializers import UnlockAttemptSerializer
from rest_framework import status
from rest_framework.response import Response

def unlock_attempt(attempt_data):
    attempt_serializer = UnlockAttemptSerializer(data=attempt_data)
    attempt_serializer.is_valid(raise_exception=True)
    attempt_serializer.save()
    
    return Response(
        attempt_data,
        status=status.HTTP_200_OK,
    )