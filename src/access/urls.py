from django.urls import path
from .views import LockViewSet, KeyViewSet, LogsViewSet, KeyLockPermissionsViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'Locks', LockViewSet, basename='lock')
router.register(r'Keys', KeyViewSet, basename='key')
router.register(r'Logs', LogsViewSet, basename='log')
router.register(r'KeyLockPermissions',
                KeyLockPermissionsViewSet, basename='key_state')

urlpatterns = [
    *router.urls,
]
