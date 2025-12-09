from django.contrib import admin
from .models import Visita, RegistroVisita, Guardia, ComunicacionGuardia, PlateRecognitionLog


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ['nombre_visitante', 'propietario', 'fecha_visita', 'codigo_acceso', 'estado']
    list_filter = ['estado', 'fecha_visita']
    search_fields = ['nombre_visitante', 'documento_identidad', 'codigo_acceso', 'placa_vehiculo']
    readonly_fields = ['codigo_acceso', 'qr_code', 'fecha_creacion']


@admin.register(RegistroVisita)
class RegistroVisitaAdmin(admin.ModelAdmin):
    list_display = ['visita', 'hora_entrada', 'hora_salida', 'guardia_registro']
    list_filter = ['hora_entrada']
    search_fields = ['visita__nombre_visitante', 'observaciones']


@admin.register(Guardia)
class GuardiaAdmin(admin.ModelAdmin):
    list_display = ['user', 'documento_identidad', 'turno', 'activo']
    list_filter = ['activo', 'turno']
    search_fields = ['user__first_name', 'user__last_name', 'documento_identidad']


@admin.register(ComunicacionGuardia)
class ComunicacionGuardiaAdmin(admin.ModelAdmin):
    list_display = ['propietario', 'guardia', 'tipo', 'fecha_solicitud', 'estado']
    list_filter = ['tipo', 'estado', 'fecha_solicitud']
    search_fields = ['mensaje', 'respuesta']


@admin.register(PlateRecognitionLog)
class PlateRecognitionLogAdmin(admin.ModelAdmin):
    list_display = [
        'plate_number', 
        'confidence', 
        'tipo_acceso', 
        'acceso_permitido',
        'fecha_reconocimiento'
    ]
    list_filter = [
        'confidence', 
        'tipo_acceso', 
        'acceso_permitido', 
        'is_registered',
        'acceso_automatico',
        'fecha_reconocimiento'
    ]
    search_fields = ['plate_number', 'observaciones']
    readonly_fields = [
        'plate_number', 
        'plate_region',
        'vehicle_type',
        'vehicle_make',
        'vehicle_model',
        'vehicle_color',
        'confidence',
        'confidence_score',
        'raw_response',
        'fecha_reconocimiento'
    ]
    fieldsets = (
        ('Información de la Placa', {
            'fields': ('plate_number', 'plate_region', 'image')
        }),
        ('Vehículo Detectado (Plate Recognizer)', {
            'fields': ('vehicle_type', 'vehicle_make', 'vehicle_model', 'vehicle_color')
        }),
        ('Confianza', {
            'fields': ('confidence', 'confidence_score')
        }),
        ('Relaciones', {
            'fields': ('vehiculo', 'unidad', 'visita', 'guardia')
        }),
        ('Control de Acceso', {
            'fields': ('is_registered', 'tipo_acceso', 'acceso_permitido', 'acceso_automatico')
        }),
        ('Metadata', {
            'fields': ('fecha_reconocimiento', 'observaciones', 'raw_response'),
            'classes': ('collapse',)
        }),
    )
