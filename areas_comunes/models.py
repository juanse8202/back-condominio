from django.db import models
from gestion.models import Propietario
import uuid

class AreaComun(models.Model):
    TIPO_COBRO = (
        ('por_hora', 'Por Hora/Persona'),
        ('pago_fijo', 'Pago Fijo por Persona'),
        ('pago_unico', 'Pago Único'),
    )
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    capacidad = models.IntegerField()
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()
    tarifa_hora = models.DecimalField(max_digits=10, decimal_places=2, help_text="Tarifa por hora/persona, pago fijo por persona o pago único")
    tipo_cobro = models.CharField(max_length=20, choices=TIPO_COBRO, default='por_hora')
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
    num_personas = models.IntegerField(default=1)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_RESERVA, default='pendiente')
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    codigo_reserva = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    
    def save(self, *args, **kwargs):
        if not self.codigo_reserva:
            self.codigo_reserva = uuid.uuid4().hex[:15].upper()
        
        # Calcular costo_total automáticamente según tipo de cobro
        # Solo calcular si aún no se ha guardado o si no tiene costo
        if self.pk is None or not self.costo_total:
            from datetime import datetime
            from decimal import Decimal
            
            # Necesitamos obtener el área desde la BD si aún no está cargada
            area = self.area if self.pk else AreaComun.objects.get(pk=self.area_id)
            
            if area.tipo_cobro == 'pago_unico':
                # Pago único sin importar personas ni horas (ej: sala de reuniones)
                self.costo_total = area.tarifa_hora
            elif area.tipo_cobro == 'pago_fijo':
                # Pago fijo por persona (ej: piscina)
                self.costo_total = area.tarifa_hora * self.num_personas
            else:
                # Por hora por persona (ej: gimnasio)
                inicio = datetime.combine(datetime.today(), self.hora_inicio)
                fin = datetime.combine(datetime.today(), self.hora_fin)
                horas = Decimal(str((fin - inicio).total_seconds() / 3600))
                self.costo_total = area.tarifa_hora * horas * self.num_personas
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.area.nombre} - {self.propietario.user.get_full_name()} - {self.fecha}"
