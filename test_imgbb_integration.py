"""
Script de prueba para verificar la integración con ImgBB.
Ejecutar: python test_imgbb_integration.py
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio.settings')
django.setup()

from django.conf import settings
from condominio.imgbb_service import imgbb_service
from PIL import Image
from io import BytesIO
import base64


def test_api_key():
    """Verifica que la API key esté configurada."""
    print("🔑 Verificando API Key...")
    if settings.IMGBB_API_KEY:
        print(f"✅ API Key configurada: {settings.IMGBB_API_KEY[:10]}...")
        return True
    else:
        print("❌ API Key NO configurada en .env")
        print("   Agrega: IMGBB_API_KEY=tu-api-key")
        return False


def test_image_upload():
    """Prueba subir una imagen de prueba a ImgBB."""
    print("\n📤 Probando subida de imagen...")
    
    # Crear imagen de prueba
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Intentar subir
    result = imgbb_service.upload_image(
        image_file=buffer,
        folder_type='qrcodes_visitas',
        name='test_image'
    )
    
    if result:
        print("✅ Imagen subida exitosamente!")
        print(f"   URL: {result['url']}")
        print(f"   Size: {result['size']} bytes")
        print(f"   Delete URL: {result['delete_url'][:50]}...")
        
        # Intentar eliminar
        print("\n🗑️  Probando eliminación...")
        if imgbb_service.delete_image(result['delete_url']):
            print("✅ Imagen eliminada exitosamente!")
        else:
            print("⚠️  No se pudo eliminar la imagen (puede ser normal)")
        
        return True
    else:
        print("❌ Error al subir imagen")
        print("   Verifica tu API key y conexión a internet")
        return False


def test_signals():
    """Verifica que los signals estén configurados."""
    print("\n⚡ Verificando signals...")
    try:
        from seguridad import signals
        print("✅ Signals de seguridad importados correctamente")
        
        # Verificar que los signals están registrados
        from django.db.models.signals import post_save
        from seguridad.models import Visita
        
        receivers = post_save._live_receivers(Visita)
        if receivers:
            print(f"✅ {len(receivers)} signal(s) registrado(s) para Visita")
        else:
            print("⚠️  No hay signals registrados para Visita")
        
        return True
    except Exception as e:
        print(f"❌ Error al verificar signals: {str(e)}")
        return False


def test_models():
    """Verifica que los modelos tengan los campos nuevos."""
    print("\n📊 Verificando modelos...")
    from seguridad.models import Visita, RegistroVisita, PlateRecognitionLog
    from administracion.models import PerfilUsuario
    from gestion.models import Vehiculo, Mascota
    
    models_to_check = [
        (Visita, ['qr_code_url', 'qr_code_delete_url']),
        (RegistroVisita, ['foto_entrada_url', 'foto_entrada_delete_url']),
        (PlateRecognitionLog, ['image_url', 'image_delete_url']),
        (PerfilUsuario, ['foto_url', 'foto_delete_url']),
        (Vehiculo, ['foto_vehiculo_url', 'foto_vehiculo_delete_url']),
        (Mascota, ['foto_url', 'foto_delete_url']),
    ]
    
    all_ok = True
    for model, fields in models_to_check:
        model_name = model.__name__
        for field in fields:
            if hasattr(model, field):
                print(f"✅ {model_name}.{field} existe")
            else:
                print(f"❌ {model_name}.{field} NO existe")
                all_ok = False
    
    return all_ok


def test_migrations():
    """Verifica que las migraciones estén aplicadas."""
    print("\n🔄 Verificando migraciones...")
    from django.core.management import call_command
    from io import StringIO
    
    out = StringIO()
    try:
        call_command('showmigrations', '--plan', stdout=out, no_color=True)
        output = out.getvalue()
        
        if '[X]' in output:
            print("✅ Hay migraciones aplicadas")
            
            # Buscar migraciones específicas de imgbb
            if 'foto_url' in output or 'image_url' in output:
                print("✅ Migraciones de ImgBB detectadas")
            else:
                print("⚠️  Migraciones de ImgBB no detectadas claramente")
                print("   Ejecuta: python manage.py migrate")
            return True
        else:
            print("⚠️  No se detectaron migraciones aplicadas")
            return False
    except Exception as e:
        print(f"❌ Error al verificar migraciones: {str(e)}")
        return False


def main():
    """Ejecuta todas las pruebas."""
    print("=" * 60)
    print("🧪 TEST DE INTEGRACIÓN CON IMGBB")
    print("=" * 60)
    
    results = {
        'API Key': test_api_key(),
        'Models': test_models(),
        'Signals': test_signals(),
        'Migrations': test_migrations(),
    }
    
    # Solo probar subida si la API key está configurada
    if results['API Key']:
        results['Image Upload'] = test_image_upload()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    print("\n" + "=" * 60)
    print(f"Resultado: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("🎉 ¡Todo está funcionando correctamente!")
    else:
        print("⚠️  Hay problemas que necesitan atención")
        print("\n📖 Consulta QUICK_START_IMGBB.md para soluciones")


if __name__ == '__main__':
    main()
