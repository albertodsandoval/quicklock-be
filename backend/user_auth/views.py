from django.shortcuts import render
from .serializer import UserSerializer
from .models import AuthUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


# Create your views here.


@api_view(['GET'])
def get_user(request):
    username = request.query_params.get("username")
    if not username:
        return Response({"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = AuthUser.objects.get(username=username)
    except AuthUser.DoesNotExist:
        return Response({"detail": "user not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def register_user(request):
    data = request.data.copy()
    data['date_joined'] = timezone.now()
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

