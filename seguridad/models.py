from django.db import models
from django.contrib.auth.models import User
from gestion.models import Propietario
import uuid
import qrcode
from io import BytesIO
from django.core.files import File

class Visita(models.Model):
    ESTADO_VISITA = (
        ('programada', 'Programada'),
        ('en_progreso', 'En Progreso'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    )
    
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='visitas')
    nombre_visitante = models.CharField(max_length=100)
    documento_identidad = models.CharField(max_length=20)
    telefono = models.CharField(max_length=15, blank=True)
    fecha_visita = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    placa_vehiculo = models.CharField(max_length=10, blank=True)
    
    codigo_acceso = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    qr_code = models.ImageField(upload_to='qrcodes_visitas/', blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_VISITA, default='programada')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.codigo_acceso:
            self.codigo_acceso = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)
        
        # Generar QR code después de guardar
        if not self.qr_code:
            self.generate_qr_code()
    
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = f"VISITA:{self.codigo_acceso}:{self.nombre_visitante}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer)
        
        self.qr_code.save(f'qr_visita_{self.codigo_acceso}.png', File(buffer), save=False)
        self.save()
    
    def __str__(self):
        return f"{self.nombre_visitante} - {self.fecha_visita}"

class RegistroVisita(models.Model):
    visita = models.ForeignKey(Visita, on_delete=models.CASCADE)
    hora_entrada = models.DateTimeField()
    hora_salida = models.DateTimeField(null=True, blank=True)
    guardia_registro = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)
    foto_entrada = models.ImageField(upload_to='fotos_visitas/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.visita.nombre_visitante} - {self.hora_entrada}"

class Guardia(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    documento_identidad = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=15)
    turno = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    fecha_contratacion = models.DateField()
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.turno}"

class ComunicacionGuardia(models.Model):
    TIPO_COMUNICACION = (
        ('llamada', 'Llamada'),
        ('chat', 'Chat'),
        ('asistencia', 'Solicitud de asistencia'),
        ('emergencia', 'Emergencia'),
    )
    
    ESTADO_COMUNICACION = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('atendida', 'Atendida'),
    )
    
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    guardia = models.ForeignKey(Guardia, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_COMUNICACION)
    mensaje = models.TextField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_atencion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_COMUNICACION, default='pendiente')
    respuesta = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.tipo} - {self.propietario.user.get_full_name()} - {self.fecha_solicitud}"
