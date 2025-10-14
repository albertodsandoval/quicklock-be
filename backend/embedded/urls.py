from django.urls import path
from . import views

urlpatterns = [
    path('index/',views.index),
    path('', views.return_card_id),
    path('latest_card/', views.latest_card),
]