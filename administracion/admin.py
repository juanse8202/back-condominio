from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Rol, PerfilUsuario, HistorialAcceso
from .services import GestorUsuarios


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'django_group', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'nombre']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion']


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ['rol', 'propietario', 'telefono', 'foto', 'activo', 'creado_automaticamente', 'cambio_password_requerido']
    readonly_fields = ['creado_automaticamente']


# Extender el UserAdmin de Django
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_rol', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'perfil__rol']
    
    def get_rol(self, obj):
        if hasattr(obj, 'perfil') and obj.perfil.rol:
            return obj.perfil.rol.get_nombre_display()
        return '-'
    get_rol.short_description = 'Rol'


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(HistorialAcceso)
class HistorialAccesoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha_hora', 'ip_address', 'exitoso']
    list_filter = ['exitoso', 'fecha_hora']
    search_fields = ['usuario__username', 'ip_address']
    readonly_fields = ['usuario', 'fecha_hora', 'ip_address', 'user_agent', 'exitoso']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
