from django.apps import AppConfig


class SeguridadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seguridad'
    
    def ready(self):
        """Importar signals al iniciar la aplicación."""
        import seguridad.signals
