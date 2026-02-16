from django.urls import path
from .views import MobileLockAccessView, CardLockAccessView, RequestStatusView, LogsByUserView, GenerateKeyView, LockViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'Locks', LockViewSet, basename='lock')

urlpatterns = [
    path('mobile_request/', MobileLockAccessView.as_view()),
    path('card_request/', CardLockAccessView.as_view()),
    path('request_status/', RequestStatusView.as_view()),
    path('user_logs/', LogsByUserView.as_view()),
    path('generate_key/', GenerateKeyView.as_view()),
    *router.urls,
]