# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import CustomTokenObtainPairView
router = DefaultRouter()

# Endpoints para móvil
router.register(r'mi-perfil', views.PropietarioViewSet, basename='mi-perfil')
router.register(r'mis-expensas', views.ExpensaViewSet, basename='mis-expensas')
router.register(r'mis-reservas', views.ReservaViewSet, basename='mis-reservas')
router.register(r'mis-visitas', views.VisitaViewSet, basename='mis-visitas')
router.register(r'mis-reportes', views.ReporteViewSet, basename='mis-reportes')

# Endpoints para web admin
router.register(r'admin/propietarios', views.AdminPropietarioViewSet, basename='admin-propietarios')
router.register(r'admin/expensas', views.AdminExpensaViewSet, basename='admin-expensas')
router.register(r'admin/reportes', views.AdminReporteViewSet, basename='admin-reportes')
router.register(r'admin/visitas', views.AdminVisitaViewSet, basename='admin-visitas')

# Endpoints para guardias
router.register(r'guardia/visitas', views.GuardiaVisitaViewSet, basename='guardia-visitas')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]


urlpatterns += [
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]