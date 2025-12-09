import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio.settings')
django.setup()

from django.contrib.auth.models import User
from gestion.models import Propietario

# Resetear contraseñas de usuarios propietarios
print("=== RESETEANDO CONTRASEÑAS ===")

for propietario in Propietario.objects.all():
    user = propietario.user
    password = propietario.documento_identidad
    user.set_password(password)
    user.save()
    print(f"\n✓ Usuario '{user.username}' actualizado")
    print(f"  - Nueva contraseña: {password}")
    print(f"  - Verificando: {user.check_password(password)}")
