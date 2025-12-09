from django.db import models
from django.contrib.auth.models import User

class Propietario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    documento_identidad = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=15)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # Control de mora
    meses_mora = models.IntegerField(default=0, help_text='Cantidad de meses en mora')
    restringido_por_mora = models.BooleanField(default=False, help_text='Restricción de acceso por mora')
    
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
    TIPO_VEHICULO_CHOICES = [
        ('sedan', 'Sedán'),
        ('suv', 'SUV'),
        ('pickup', 'Pickup'),
        ('hatchback', 'Hatchback'),
        ('camioneta', 'Camioneta'),
        ('van', 'Van'),
        ('coupe', 'Coupé'),
        ('convertible', 'Convertible'),
        ('minivan', 'Minivan'),
        ('crossover', 'Crossover'),
    ]
    
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name='vehiculos')
    unidad = models.ForeignKey('UnidadHabitacional', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehiculos')
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    tipo = models.CharField(max_length=20, choices=TIPO_VEHICULO_CHOICES, blank=True, null=True)
    año = models.IntegerField(null=True, blank=True)
    foto_vehiculo = models.ImageField(upload_to='vehiculos/', null=True, blank=True)
    foto_vehiculo_url = models.URLField(max_length=500, blank=True, null=True, help_text='URL de foto en ImgBB')
    foto_vehiculo_delete_url = models.URLField(max_length=500, blank=True, null=True, help_text='URL para eliminar foto de ImgBB')
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_registro']
    
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
    foto_url = models.URLField(max_length=500, blank=True, null=True, help_text='URL de foto en ImgBB')
    foto_delete_url = models.URLField(max_length=500, blank=True, null=True, help_text='URL para eliminar foto de ImgBB')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.tipo}"
