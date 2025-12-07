from django.contrib import admin
from .models import Propietario, UnidadHabitacional, Vehiculo, Mascota


@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    list_display = ['documento_identidad', 'get_nombre', 'telefono', 'fecha_registro']
    search_fields = ['documento_identidad', 'user__first_name', 'user__last_name', 'telefono']
    list_filter = ['fecha_registro']
    
    def get_nombre(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_nombre.short_description = 'Nombre Completo'


@admin.register(UnidadHabitacional)
class UnidadHabitacionalAdmin(admin.ModelAdmin):
    list_display = ['numero', 'edificio', 'tipo', 'piso', 'get_propietario']
    search_fields = ['numero', 'edificio', 'propietario__user__first_name']
    list_filter = ['tipo', 'edificio']
    
    def get_propietario(self, obj):
        return obj.propietario.user.get_full_name()
    get_propietario.short_description = 'Propietario'


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'marca', 'modelo', 'color', 'get_propietario', 'fecha_registro']
    search_fields = ['placa', 'marca', 'modelo', 'propietario__user__first_name']
    list_filter = ['marca', 'fecha_registro']
    
    def get_propietario(self, obj):
        return obj.propietario.user.get_full_name()
    get_propietario.short_description = 'Propietario'


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'raza', 'get_propietario']
    search_fields = ['nombre', 'raza', 'propietario__user__first_name']
    list_filter = ['tipo']
    
    def get_propietario(self, obj):
        return obj.propietario.user.get_full_name()
    get_propietario.short_description = 'Propietario'
