from django.apps import AppConfig


class AdministracionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'administracion'
    verbose_name = 'Administración de Usuarios y Roles'
    
    def ready(self):
        try:
            import administracion.signals  # Importar signals si los hay
        except ImportError:
            pass
