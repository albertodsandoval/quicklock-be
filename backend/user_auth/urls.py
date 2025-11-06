from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register_user/', views.register_user),
    path('get_user/', views.get_user),    
]