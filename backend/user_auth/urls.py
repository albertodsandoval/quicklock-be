from django.urls import path, include
from .views import UserInfoView, RegisterUserView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,   # login (get access+refresh)
    TokenRefreshView,      # rotate/refresh access using refresh
    TokenVerifyView,       # verify a token’s signature/expiry
)

urlpatterns = [
    path('register_user/', RegisterUserView.as_view()),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("user_info/", UserInfoView.as_view())
]