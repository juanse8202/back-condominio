from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropietarioViewSet, UnidadHabitacionalViewSet, VehiculoViewSet, MascotaViewSet,
    dashboard_resumen, dashboard_finanzas, dashboard_areas_comunes,
    dashboard_riesgos, dashboard_predicciones
)

router = DefaultRouter()
router.register(r'propietarios', PropietarioViewSet, basename='propietario')
router.register(r'unidades', UnidadHabitacionalViewSet, basename='unidad')
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')
router.register(r'mascotas', MascotaViewSet, basename='mascota')

urlpatterns = [
    path('', include(router.urls)),
    # Dashboard endpoints
    path('dashboard/resumen/', dashboard_resumen, name='dashboard-resumen'),
    path('dashboard/finanzas/', dashboard_finanzas, name='dashboard-finanzas'),
    path('dashboard/areas-comunes/', dashboard_areas_comunes, name='dashboard-areas-comunes'),
    path('dashboard/riesgos/', dashboard_riesgos, name='dashboard-riesgos'),
    path('dashboard/predicciones/', dashboard_predicciones, name='dashboard-predicciones'),
]
