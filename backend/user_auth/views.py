from .serializer import RegistrationSerializer, SendEmailSerializer 
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from pathlib import Path
from rest_framework.views import APIView
from rest_framework import status, permissions


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
        
        if serializer.validated_data['admin'] == True:
            user.is_staff = True

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


class UserByEmailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):

        user_email = request.data.get('user_email')

        user = User.objects.filter(email = user_email).first()

        return Response(
            {
                "username": user.username
            }, 
            status = status.HTTP_200_OK
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