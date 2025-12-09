from django.contrib.auth.models import User, Group
from django.db import transaction
from .models import Rol, PerfilUsuario
import re


class GestorUsuarios:
    """
    Servicio para crear y gestionar usuarios del sistema.
    Especialmente para creación automática de usuarios de propietarios.
    """
    
    @staticmethod
    def normalizar_nombre(nombre_completo):
        """
        Extrae el primer nombre y lo normaliza para username.
        Ej: "Juan Carlos Pérez" -> "juan"
        """
        if not nombre_completo:
            return None
        
        # Tomar el primer nombre
        primer_nombre = nombre_completo.strip().split()[0]
        
        # Normalizar: minúsculas, sin acentos, sin espacios
        primer_nombre = primer_nombre.lower()
        primer_nombre = re.sub(r'[áàäâ]', 'a', primer_nombre)
        primer_nombre = re.sub(r'[éèëê]', 'e', primer_nombre)
        primer_nombre = re.sub(r'[íìïî]', 'i', primer_nombre)
        primer_nombre = re.sub(r'[óòöô]', 'o', primer_nombre)
        primer_nombre = re.sub(r'[úùüû]', 'u', primer_nombre)
        primer_nombre = re.sub(r'[^a-z0-9]', '', primer_nombre)
        
        return primer_nombre
    
    @staticmethod
    def generar_username_unico(nombre_base):
        """
        Genera un username único agregando números si es necesario.
        Ej: "juan" -> "juan", "juan2", "juan3"...
        """
        username = nombre_base
        contador = 2
        
        while User.objects.filter(username=username).exists():
            username = f"{nombre_base}{contador}"
            contador += 1
        
        return username
    
    @staticmethod
    @transaction.atomic
    def crear_usuario_propietario(propietario):
        """
        Crea un usuario para un propietario automáticamente.
        
        Args:
            propietario: Instancia del modelo Propietario
        
        Returns:
            tuple: (user, password, created)
            - user: Instancia del User creado
            - password: La contraseña generada (carnet)
            - created: True si se creó, False si ya existía
        """
        # Verificar si ya tiene usuario
        if hasattr(propietario, 'perfil_usuario') and propietario.perfil_usuario:
            return (propietario.perfil_usuario.user, None, False)
        
        # Generar username desde el primer nombre
        nombre_base = GestorUsuarios.normalizar_nombre(propietario.nombre)
        if not nombre_base:
            raise ValueError("El propietario debe tener un nombre válido")
        
        username = GestorUsuarios.generar_username_unico(nombre_base)
        
        # La contraseña es el número de carnet/CI
        password = str(propietario.ci).strip()
        if not password:
            raise ValueError("El propietario debe tener un número de carnet/CI válido")
        
        # Obtener o crear el rol de PROPIETARIO
        rol_propietario, _ = Rol.objects.get_or_create(
            nombre='PROPIETARIO',
            defaults={
                'descripcion': 'Propietario de unidad habitacional',
                'django_group': Group.objects.get_or_create(name='Propietarios')[0]
            }
        )
        
        # Crear el usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=propietario.nombre.split()[0] if propietario.nombre else '',
            last_name=' '.join(propietario.nombre.split()[1:]) if propietario.nombre and len(propietario.nombre.split()) > 1 else '',
            email=propietario.email or '',
            is_active=True,
            is_staff=False,
            is_superuser=False
        )
        
        # Asignar al grupo
        user.groups.add(rol_propietario.django_group)
        
        # Actualizar el perfil
        perfil = user.perfil
        perfil.rol = rol_propietario
        perfil.propietario = propietario
        perfil.telefono = propietario.telefono
        perfil.creado_automaticamente = True
        perfil.cambio_password_requerido = True  # Forzar cambio en primer login
        perfil.save()
        
        return (user, password, True)
    
    @staticmethod
    @transaction.atomic
    def crear_usuario_staff(username, password, email, rol_nombre, **kwargs):
        """
        Crea un usuario de staff (admin, guardia).
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            email: Email
            rol_nombre: Uno de: ADMIN, GUARDIA
            **kwargs: first_name, last_name, telefono, etc.
        
        Returns:
            User: Instancia del usuario creado
        """
        # Verificar que el username no exista
        if User.objects.filter(username=username).exists():
            raise ValueError(f"El username '{username}' ya existe")
        
        # Obtener o crear el rol
        rol, _ = Rol.objects.get_or_create(
            nombre=rol_nombre,
            defaults={
                'descripcion': dict(Rol.ROLES_CHOICES).get(rol_nombre, ''),
                'django_group': Group.objects.get_or_create(name=dict(Rol.ROLES_CHOICES).get(rol_nombre, rol_nombre))[0]
            }
        )
        
        # Determinar permisos según rol
        is_staff = rol_nombre in ['ADMIN', 'CONTADOR']
        is_superuser = rol_nombre == 'ADMIN'
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=kwargs.get('first_name', ''),
            last_name=kwargs.get('last_name', ''),
            is_active=True,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        
        # Asignar al grupo
        user.groups.add(rol.django_group)
        
        # Actualizar perfil
        perfil = user.perfil
        perfil.rol = rol
        perfil.telefono = kwargs.get('telefono', '')
        perfil.save()
        
        return user
    
    @staticmethod
    def cambiar_password(user, nueva_password):
        """
        Cambia la contraseña del usuario y marca que ya no requiere cambio.
        """
        user.set_password(nueva_password)
        user.save()
        
        if hasattr(user, 'perfil'):
            user.perfil.cambio_password_requerido = False
            user.perfil.save()
    
    @staticmethod
    def desactivar_usuario(user):
        """
        Desactiva un usuario (no lo elimina).
        """
        user.is_active = False
        user.save()
        
        if hasattr(user, 'perfil'):
            user.perfil.activo = False
            user.perfil.save()
    
    @staticmethod
    def activar_usuario(user):
        """
        Activa un usuario desactivado.
        """
        user.is_active = True
        user.save()
        
        if hasattr(user, 'perfil'):
            user.perfil.activo = True
            user.perfil.save()
