from django.urls import path, include
from . import views
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,   # login (get access+refresh)
    TokenRefreshView,      # rotate/refresh access using refresh
    TokenVerifyView,       # verify a token’s signature/expiry
)

class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    authentication_classes = ()  # <— important: no SessionAuthentication

urlpatterns = [
    path('register_user/', views.register_user),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("test_email/", views.send_email),
]