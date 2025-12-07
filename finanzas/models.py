from django.db import models
from gestion.models import Propietario

class Expensa(models.Model):
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    mes_referencia = models.CharField(max_length=7)  # Formato: YYYY-MM
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    cuota_basica = models.DecimalField(max_digits=10, decimal_places=2)
    multas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reservas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    otros = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    pagada = models.BooleanField(default=False)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Expensa {self.mes_referencia} - {self.propietario.user.get_full_name()}"

class Pago(models.Model):
    METODO_PAGO = (
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('efectivo', 'Efectivo'),
    )
    
    expensa = models.ForeignKey(Expensa, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO)
    referencia = models.CharField(max_length=100, unique=True)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    comprobante = models.FileField(upload_to='comprobantes_pagos/', null=True, blank=True)
    verificado = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Pago {self.referencia} - {self.monto}"
