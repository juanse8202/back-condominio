from django.db import models
from gestion.models import Propietario
import uuid

class AreaComun(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    capacidad = models.IntegerField()
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()
    tarifa_hora = models.DecimalField(max_digits=10, decimal_places=2)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

class ReservaAreaComun(models.Model):
    ESTADO_RESERVA = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    )
    
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    area = models.ForeignKey(AreaComun, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_RESERVA, default='pendiente')
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    codigo_reserva = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    
    def save(self, *args, **kwargs):
        if not self.codigo_reserva:
            self.codigo_reserva = uuid.uuid4().hex[:15].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.area.nombre} - {self.propietario.user.get_full_name()} - {self.fecha}"
