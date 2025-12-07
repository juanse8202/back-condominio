from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VisitaViewSet, RegistroVisitaViewSet, GuardiaViewSet, ComunicacionGuardiaViewSet

router = DefaultRouter()
router.register(r'visitas', VisitaViewSet, basename='visita')
router.register(r'registros', RegistroVisitaViewSet, basename='registro-visita')
router.register(r'guardias', GuardiaViewSet, basename='guardia')
router.register(r'comunicaciones', ComunicacionGuardiaViewSet, basename='comunicacion-guardia')

urlpatterns = [
    path('', include(router.urls)),
]
