from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RolViewSet, UserViewSet, HistorialAccesoViewSet

router = DefaultRouter()
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'users', UserViewSet, basename='user')
router.register(r'historial-accesos', HistorialAccesoViewSet, basename='historial-acceso')

urlpatterns = [
    path('', include(router.urls)),
]
