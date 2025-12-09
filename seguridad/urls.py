from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VisitaViewSet, 
    RegistroVisitaViewSet, 
    GuardiaViewSet, 
    ComunicacionGuardiaViewSet,
    PlateRecognitionLogViewSet
)

router = DefaultRouter()
router.register(r'visitas', VisitaViewSet, basename='visita')
router.register(r'registros', RegistroVisitaViewSet, basename='registro-visita')
router.register(r'guardias', GuardiaViewSet, basename='guardia')
router.register(r'comunicaciones', ComunicacionGuardiaViewSet, basename='comunicacion-guardia')
router.register(r'plate-recognition-logs', PlateRecognitionLogViewSet, basename='plate-recognition-log')

urlpatterns = [
    path('', include(router.urls)),
]
