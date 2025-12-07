from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComunicadoViewSet

router = DefaultRouter()
router.register(r'comunicados', ComunicadoViewSet, basename='comunicado')

urlpatterns = [
    path('', include(router.urls)),
]
