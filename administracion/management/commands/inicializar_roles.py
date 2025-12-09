from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from administracion.models import Rol


class Command(BaseCommand):
    help = 'Inicializa los roles por defecto del sistema'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando creación de roles...')
        
        roles_config = [
            ('ADMIN', 'Administrador del sistema con acceso total'),
            ('PROPIETARIO', 'Propietario de unidad habitacional'),
            ('INQUILINO', 'Inquilino de unidad habitacional'),
            ('GUARDIA', 'Guardia de seguridad'),
        ]
        
        for rol_nombre, descripcion in roles_config:
            # Crear o obtener el Group de Django
            group_name = dict(Rol.ROLES_CHOICES).get(rol_nombre, rol_nombre)
            group, group_created = Group.objects.get_or_create(name=group_name)
            
            if group_created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Group "{group_name}" creado'))
            
            # Crear o obtener el Rol personalizado
            rol, rol_created = Rol.objects.get_or_create(
                nombre=rol_nombre,
                defaults={
                    'descripcion': descripcion,
                    'django_group': group,
                    'activo': True
                }
            )
            
            if rol_created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Rol "{rol.get_nombre_display()}" creado'))
            else:
                self.stdout.write(f'  - Rol "{rol.get_nombre_display()}" ya existe')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Inicialización de roles completada'))
