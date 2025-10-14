from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('embedded/', views.return_card_id),
    path('embedded/latest_card/', views.latest_card),
]