from django.urls import path, include
from .views import UserInfoView, RegisterUserView, SendEmailView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register_user/', RegisterUserView.as_view()),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("test_email/", SendEmailView.as_view()),
    path("user_info/", UserInfoView.as_view())
]