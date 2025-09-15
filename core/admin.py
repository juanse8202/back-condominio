from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import *

class PropietarioInline(admin.StackedInline):
    model = Propietario
    can_delete = False
    verbose_name_plural = 'Propietarios'

class CustomUserAdmin(UserAdmin):
    inlines = (PropietarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_documento')
    
    def get_documento(self, obj):
        try:
            return obj.propietario.documento_identidad
        except:
            return "N/A"
    get_documento.short_description = 'Documento'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'documento_identidad', 'telefono', 'fecha_registro')
    search_fields = ('user__first_name', 'user__last_name', 'documento_identidad')
    list_filter = ('fecha_registro',)

@admin.register(UnidadHabitacional)
class UnidadHabitacionalAdmin(admin.ModelAdmin):
    list_display = ('numero', 'edificio', 'tipo', 'piso', 'propietario')
    list_filter = ('tipo', 'edificio')
    search_fields = ('numero', 'propietario__user__first_name', 'propietario__user__last_name')

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'marca', 'modelo', 'color', 'propietario')
    search_fields = ('placa', 'propietario__user__first_name')
    list_filter = ('marca', 'color')

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'raza', 'propietario')
    list_filter = ('tipo',)
    search_fields = ('nombre', 'propietario__user__first_name')

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'propietario', 'estado', 'prioridad', 'fecha_reporte')
    list_filter = ('tipo', 'estado', 'prioridad', 'fecha_reporte')
    search_fields = ('titulo', 'propietario__user__first_name')
    readonly_fields = ('fecha_reporte',)

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('nombre_visitante', 'documento_identidad', 'propietario', 'fecha_visita', 'estado')
    list_filter = ('estado', 'fecha_visita')
    search_fields = ('nombre_visitante', 'documento_identidad', 'propietario__user__first_name')
    readonly_fields = ('codigo_acceso', 'fecha_creacion')

@admin.register(RegistroVisita)
class RegistroVisitaAdmin(admin.ModelAdmin):
    list_display = ('visita', 'hora_entrada', 'hora_salida', 'guardia_registro')
    list_filter = ('hora_entrada',)
    readonly_fields = ('hora_entrada',)

@admin.register(AreaComun)
class AreaComunAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'tarifa_hora', 'activa')
    list_filter = ('activa',)

@admin.register(ReservaAreaComun)
class ReservaAreaComunAdmin(admin.ModelAdmin):
    list_display = ('area', 'propietario', 'fecha', 'hora_inicio', 'estado', 'costo_total')
    list_filter = ('estado', 'fecha', 'area')
    search_fields = ('propietario__user__first_name', 'area__nombre')
    readonly_fields = ('codigo_reserva', 'fecha_reserva')

@admin.register(Expensa)
class ExpensaAdmin(admin.ModelAdmin):
    list_display = ('propietario', 'mes_referencia', 'monto_total', 'fecha_vencimiento', 'pagada')
    list_filter = ('pagada', 'fecha_emision', 'mes_referencia')
    search_fields = ('propietario__user__first_name', 'mes_referencia')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('expensa', 'monto', 'metodo_pago', 'fecha_pago')
    list_filter = ('metodo_pago', 'fecha_pago')
    readonly_fields = ('fecha_pago',)

@admin.register(Guardia)
class GuardiaAdmin(admin.ModelAdmin):
    list_display = ('user', 'documento_identidad', 'telefono', 'turno', 'activo')
    list_filter = ('turno', 'activo')
    search_fields = ('user__first_name', 'documento_identidad')

@admin.register(ComunicacionGuardia)
class ComunicacionGuardiaAdmin(admin.ModelAdmin):
    list_display = ('propietario', 'tipo', 'estado', 'fecha_solicitud')
    list_filter = ('tipo', 'estado', 'fecha_solicitud')
    readonly_fields = ('fecha_solicitud',)