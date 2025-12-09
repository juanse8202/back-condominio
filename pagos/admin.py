from django.contrib import admin
from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'propietario',
        'tipo_pago',
        'monto',
        'estado',
        'fecha_creacion',
        'fecha_completado',
    ]
    list_filter = ['estado', 'tipo_pago', 'fecha_creacion']
    search_fields = [
        'propietario__usuario__username',
        'propietario__usuario__email',
        'payment_intent_id',
        'charge_id',
    ]
    readonly_fields = [
        'payment_intent_id',
        'payment_method_id',
        'charge_id',
        'fecha_creacion',
        'fecha_actualizacion',
        'fecha_completado',
    ]
    
    fieldsets = (
        ('Información General', {
            'fields': ('propietario', 'reserva', 'tipo_pago', 'descripcion')
        }),
        ('Monto', {
            'fields': ('monto', 'moneda')
        }),
        ('Stripe', {
            'fields': (
                'payment_intent_id',
                'payment_method_id',
                'charge_id',
                'estado',
            )
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion',
                'fecha_completado',
            ),
            'classes': ('collapse',)
        }),
    )
