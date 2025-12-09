from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from administracion.views import UserViewSet

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 AUTH
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/me/', UserViewSet.as_view({'get': 'me'}), name='user_me'),

    # ✅ PAGOS SIEMPRE ARRIBA (ANTES DE LOS path('api/', include(...)))
    path('api/pagos/', include('pagos.urls')),

    # ✅ RESTO DE MÓDULOS
    path('api/administracion/', include('administracion.urls')),
    path('api/seguridad/', include('seguridad.urls')),

    # ⚠️ LOS GENERALES 'api/' SIEMPRE AL FINAL
    path('api/', include('gestion.urls')),
    path('api/', include('finanzas.urls')),
    path('api/', include('areas_comunes.urls')),
    path('api/', include('comunicacion.urls')),
    path('api/', include('mantenimiento.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
