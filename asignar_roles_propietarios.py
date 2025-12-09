"""
Script para asignar roles PROPIETARIO a los usuarios que están vinculados a propietarios.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio.settings')
django.setup()

from django.contrib.auth.models import User
from administracion.models import PerfilUsuario, Rol
from gestion.models import Propietario

def asignar_roles_propietarios():
    """
    Asigna el rol PROPIETARIO a todos los usuarios que tengan un registro de Propietario.
    """
    print("🔄 Buscando propietarios sin rol asignado...")
    
    try:
        rol_propietario = Rol.objects.get(nombre='PROPIETARIO', activo=True)
        print(f"✅ Rol PROPIETARIO encontrado\n")
    except Rol.DoesNotExist:
        print("❌ Error: El rol PROPIETARIO no existe. Ejecuta: python manage.py inicializar_roles")
        return
    
    propietarios = Propietario.objects.select_related('user').all()
    asignados = 0
    ya_tenian = 0
    
    for propietario in propietarios:
        user = propietario.user
        
        # Obtener o crear perfil
        perfil, created = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={'propietario': propietario}
        )
        
        # Vincular propietario al perfil si no está vinculado
        if not perfil.propietario:
            perfil.propietario = propietario
            perfil.save()
        
        # Asignar rol si no tiene
        if not perfil.rol:
            perfil.rol = rol_propietario
            perfil.save()
            
            # Agregar al grupo de Django
            user.groups.clear()
            user.groups.add(rol_propietario.django_group)
            
            asignados += 1
            print(f"✅ Rol PROPIETARIO asignado a: {user.username} ({user.get_full_name()})")
        else:
            ya_tenian += 1
            print(f"ℹ️  {user.username} ya tiene rol: {perfil.rol.get_nombre_display()}")
    
    print("\n" + "="*60)
    print(f"📊 Resumen:")
    print(f"   Total propietarios: {propietarios.count()}")
    print(f"   Roles asignados: {asignados}")
    print(f"   Ya tenían rol: {ya_tenian}")
    print("="*60)

if __name__ == '__main__':
    asignar_roles_propietarios()
