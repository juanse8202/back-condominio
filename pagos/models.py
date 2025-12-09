from django.db import models
from gestion.models import Propietario
from areas_comunes.models import ReservaAreaComun


class Pago(models.Model):
    """Modelo para registrar pagos procesados por Stripe"""
    
    TIPO_PAGO_CHOICES = [
        ('reserva', 'Reserva de Área'),
        ('expensa', 'Expensa'),
        ('multa', 'Multa'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Relaciones
    propietario = models.ForeignKey(
        Propietario,
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    reserva = models.ForeignKey(
        ReservaAreaComun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos'
    )
    
    # Información del pago
    tipo_pago = models.CharField(
        max_length=20,
        choices=TIPO_PAGO_CHOICES,
        default='reserva'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    moneda = models.CharField(
        max_length=3,
        default='BOB'
    )
    
    # Información de Stripe
    payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        help_text='ID del Payment Intent de Stripe'
    )
    payment_method_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='ID del método de pago de Stripe'
    )
    charge_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='ID del cargo de Stripe'
    )
    
    # Estado y metadatos
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_PAGO_CHOICES,
        default='pendiente'
    )
    descripcion = models.TextField(blank=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Información adicional del pago'
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'pagos'
        ordering = ['-fecha_creacion']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        indexes = [
            models.Index(fields=['propietario', '-fecha_creacion']),
            models.Index(fields=['payment_intent_id']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"Pago {self.id} - {self.propietario.usuario.username} - Bs {self.monto}"
