from django.db import models
from django.contrib.auth.models import User

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
