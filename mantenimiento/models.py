from django.db import models
from gestion.models import Propietario

class Reporte(models.Model):
    TIPO_REPORTE = (
        ('incumplimiento', 'Incumplimiento de reglas'),
        ('mantenimiento', 'Problema de mantenimiento'),
        ('seguridad', 'Incidente de seguridad'),
        ('ruido', 'Ruido molesto'),
        ('limpieza', 'Problema de limpieza'),
        ('otro', 'Otro'),
    )
    
    ESTADO_REPORTE = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('rechazado', 'Rechazado'),
    )
    
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_REPORTE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='reportes/', null=True, blank=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_REPORTE, default='pendiente')
    prioridad = models.IntegerField(default=1)  # 1-5, siendo 5 la más alta
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"
