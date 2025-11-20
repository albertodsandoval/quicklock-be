from django.shortcuts import render
from .serializer import UserSerializer
from .models import AuthUser
from django.contrib.auth.models import User
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
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response({"detail": "username, email, and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"detail": "username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    return Response({"detail": f"User {user.username} created successfully"}, status=status.HTTP_201_CREATED)