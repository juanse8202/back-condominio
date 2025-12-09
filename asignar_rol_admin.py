"""
Script para asignar el rol ADMIN al usuario admin si no tiene rol.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio.settings')
django.setup()

from django.contrib.auth.models import User
from administracion.models import PerfilUsuario, Rol

def asignar_rol_admin():
    """
    Asigna el rol ADMIN al usuario admin si existe.
    """
    print("🔄 Buscando usuario admin...")
    
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuario admin encontrado (ID: {admin_user.id})")
        
        # Obtener o crear perfil
        perfil, created = PerfilUsuario.objects.get_or_create(user=admin_user)
        
        if created:
            print("✨ Perfil creado para admin")
        
        # Obtener rol ADMIN
        try:
            rol_admin = Rol.objects.get(nombre='ADMIN', activo=True)
            
            if perfil.rol:
                print(f"ℹ️  Admin ya tiene el rol: {perfil.rol.get_nombre_display()}")
            else:
                perfil.rol = rol_admin
                perfil.save()
                
                # Agregar al grupo de Django
                admin_user.groups.clear()
                admin_user.groups.add(rol_admin.django_group)
                
                print(f"✅ Rol ADMIN asignado exitosamente a {admin_user.username}")
                
        except Rol.DoesNotExist:
            print("❌ Error: El rol ADMIN no existe. Ejecuta: python manage.py inicializar_roles")
            
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado")

if __name__ == '__main__':
    asignar_rol_admin()
