from .serializer import RegistrationSerializer, SendEmailSerializer
from access.serializers import KeyGenerationSerializer
from django.contrib.auth.models import User
from access.models import Locks, AuthUser, Keys, KeyLockPermissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from pathlib import Path
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.utils import timezone
import uuid


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
            return Response(
                {"detail": "username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username, email=email, password=password)

        user.save()
        user = AuthUser.objects.get(pk=user.pk)

        if serializer.validated_data['admin'] is True:
            user.is_staff = True
            user.save()

            lock = Locks.objects.get(pk=1)
            lock.administrator = user
            lock.save()

            key_serializer = KeyGenerationSerializer(data={
                "user_email": email,
                "lock_id": lock.lock_id,
                "administrator": user.pk,
                "credential": str(uuid.uuid4()),
                "key_name": f"{username}'s default key",
                "not_valid_before": timezone.now(),
                "not_valid_after": timezone.now() + timezone.timedelta(days=3650),
                "is_revoked": False,
            })

            key_serializer.is_valid(raise_exception=True)
            key_serializer.save()

        file_path = Path(settings.BASE_DIR) / "user_auth" / \
            "registration_email.txt"

        # try:
        #     send_mail(
        #         "Welcome to QuickLock!",
        #         import_file(file_path),
        #         settings.DEFAULT_FROM_EMAIL,
        #         [email],
        #         fail_silently=False,
        #     )
        # except Exception as e:
        #     print(f"Email failed: {e}")

        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )


class UserByEmailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):

        user_email = request.data.get('user_email')

        user = User.objects.filter(email=user_email).first()

        return Response(
            {
                "username": user.username,
                "user_id": user.pk
            },
            status=status.HTTP_200_OK
        )


# file importer
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
