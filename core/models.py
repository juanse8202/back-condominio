from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import uuid
import qrcode
from io import BytesIO
from django.core.files import File

class Propietario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    documento_identidad = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=15)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.documento_identidad}"

class UnidadHabitacional(models.Model):
    TIPO_UNIDAD = (
        ('casa', 'Casa'),
        ('departamento', 'Departamento'),
        ('penthouse', 'Penthouse'),
    )
    
    propietario = models.OneToOneField(Propietario, on_delete=models.CASCADE, related_name='unidad')
    numero = models.CharField(max_length=10)
    edificio = models.CharField(max_length=50, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_UNIDAD)
    piso = models.IntegerField(null=True, blank=True)
    caracteristicas = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.tipo} {self.numero} - {self.edificio}"

class Vehiculo(models.Model):
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='vehiculos')
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"

class Mascota(models.Model):
    TIPO_MASCOTA = (
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('ave', 'Ave'),
        ('otro', 'Otro'),
    )
    
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='mascotas')
    nombre = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPO_MASCOTA)
    raza = models.CharField(max_length=50, blank=True)
    foto = models.ImageField(upload_to='mascotas/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.tipo}"

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
    
    def __str__(self):
        return f"Pago {self.referencia} - {self.monto}"

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