from django.shortcuts import render
from .serializer import UserSerializer
from .models import AuthUser
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
import json
from pathlib import Path
from django.utils import timezone


# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny])
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


    file_path = Path(settings.BASE_DIR) / "user_auth" / "registration_email.txt"

    try:
        send_mail(
            "Welcome to QuickLock!",
            import_file(file_path),
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response({"detail": f"User {user.username} created successfully"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def send_email(request):

    email = request.data.get("email")

    file_path = Path(settings.BASE_DIR) / "user_auth" / "registration_email.txt"

    try:
        send_mail(
            "Welcome to QuickLock!",
            import_file(file_path),
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response({"message": "Email sent successfully!"})

    except Exception as e:
        return Response({"error": str(e)}, status=500)


def import_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return ""  # fall back safely
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""