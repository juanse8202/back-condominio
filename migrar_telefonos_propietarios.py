"""
Script para migrar los teléfonos de los propietarios a sus perfiles de usuario.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio.settings')
django.setup()

from gestion.models import Propietario
from administracion.models import PerfilUsuario

def migrar_telefonos():
    """
    Migra los teléfonos de la tabla Propietario a PerfilUsuario.
    """
    print("🔄 Iniciando migración de teléfonos...")
    
    propietarios = Propietario.objects.select_related('user').all()
    total = propietarios.count()
    migrados = 0
    sin_perfil = 0
    
    for propietario in propietarios:
        try:
            # Obtener o crear el perfil del usuario
            perfil, created = PerfilUsuario.objects.get_or_create(
                user=propietario.user
            )
            
            # Si el propietario tiene teléfono y el perfil no lo tiene, migrarlo
            if propietario.telefono and not perfil.telefono:
                perfil.telefono = propietario.telefono
                perfil.save()
                migrados += 1
                print(f"✅ Migrado teléfono de {propietario.user.username}: {propietario.telefono}")
            elif perfil.telefono:
                print(f"ℹ️  {propietario.user.username} ya tiene teléfono en perfil: {perfil.telefono}")
            else:
                print(f"⚠️  {propietario.user.username} no tiene teléfono en Propietario")
                
        except Exception as e:
            sin_perfil += 1
            print(f"❌ Error con {propietario.user.username}: {str(e)}")
    
    print("\n" + "="*60)
    print(f"📊 Resumen de migración:")
    print(f"   Total propietarios: {total}")
    print(f"   Teléfonos migrados: {migrados}")
    print(f"   Errores: {sin_perfil}")
    print("="*60)

if __name__ == '__main__':
    migrar_telefonos()
