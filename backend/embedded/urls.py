from django.urls import path
from .views import MobileLockAccessView, CardLockAccessView, RequestStatusView

urlpatterns = [
    path('mobile_request/', MobileLockAccessView.as_view()),
    path('card_request/', CardLockAccessView.as_view()),
    path('request_status/', RequestStatusView.as_view()),
]