from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AreaComunViewSet, ReservaAreaComunViewSet

router = DefaultRouter()
router.register(r'areas', AreaComunViewSet, basename='area')
router.register(r'reservas', ReservaAreaComunViewSet, basename='reserva')

urlpatterns = [
    path('', include(router.urls)),
]
