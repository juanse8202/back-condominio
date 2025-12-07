from django.db import models
from django.contrib.auth.models import User

class Comunicado(models.Model):
    TIPO_COMUNICADO = (
        ('aviso', 'Aviso'),
        ('noticia', 'Noticia'),
        ('evento', 'Evento'),
        ('urgente', 'Urgente'),
    )
    
    PRIORIDAD = (
        (1, 'Baja'),
        (2, 'Media'),
        (3, 'Alta'),
    )
    
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_COMUNICADO)
    prioridad = models.IntegerField(choices=PRIORIDAD, default=2)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='comunicados/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_display()}"
