from django.shortcuts import render
from .serializer import UserSerializer, RegistrationSerializer
from .models import AuthUser
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from pathlib import Path
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework import status, permissions
import json


class UserInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        username = request.user.username
        email = request.user.email

        return Response(
                {
                    "username": username,
                    "email": email,
                },
            )
 

class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):

        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
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
            return Response({"message": "Email sent successfully!"})

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