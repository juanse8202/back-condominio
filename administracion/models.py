from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

class Rol(models.Model):
    """
    Modelo para definir roles personalizados del sistema.
    Se vincula con los Groups de Django para permisos.
    """
    ROLES_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('PROPIETARIO', 'Propietario'),
        ('INQUILINO', 'Inquilino'),
        ('GUARDIA', 'Guardia de Seguridad'),
    ]
    
    nombre = models.CharField(max_length=50, choices=ROLES_CHOICES, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    django_group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='rol_custom')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_nombre_display()


class PerfilUsuario(models.Model):
    """
    Extensión del modelo User de Django para información adicional.
    Vincula usuarios con roles y propietarios.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    
    # Vinculación con Propietario (si aplica)
    propietario = models.OneToOneField(
        'gestion.Propietario', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='perfil_usuario'
    )
    
    telefono = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True)
    foto_url = models.URLField(max_length=500, blank=True, null=True, help_text='URL de foto en ImgBB')
    foto_delete_url = models.URLField(max_length=500, blank=True, null=True, help_text='URL para eliminar foto de ImgBB')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    # Datos de creación automática
    creado_automaticamente = models.BooleanField(default=False)
    cambio_password_requerido = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.rol}"


class HistorialAcceso(models.Model):
    """
    Registro de accesos al sistema para auditoría.
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historial_accesos')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    exitoso = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Historial de Acceso'
        verbose_name_plural = 'Historiales de Acceso'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"


# Signal para crear perfil automáticamente cuando se crea un User
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea automáticamente un PerfilUsuario cuando se crea un User.
    """
    if created:
        PerfilUsuario.objects.create(user=instance)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Guarda el perfil cuando se actualiza el User.
    """
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
