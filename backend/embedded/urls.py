from django.urls import path
from .views import MobileLockAccessView, CardLockAccessView, RequestStatusView, LogsByUserView, GenerateKeyView

urlpatterns = [
    path('mobile_request/', MobileLockAccessView.as_view()),
    path('card_request/', CardLockAccessView.as_view()),
    path('request_status/', RequestStatusView.as_view()),
    path('user_logs/', LogsByUserView.as_view()),
    path('generate_key/', GenerateKeyView.as_view())
]