import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condominio.settings')
django.setup()

from django.contrib.auth.models import User
from gestion.models import Propietario

# Verificar usuarios
print("=== USUARIOS EN LA BASE DE DATOS ===")
users = User.objects.all()
for u in users:
    print(f"\nUsuario: {u.username}")
    print(f"  - Email: {u.email}")
    print(f"  - Activo: {u.is_active}")
    print(f"  - Nombre: {u.first_name} {u.last_name}")

# Verificar propietarios
print("\n=== PROPIETARIOS EN LA BASE DE DATOS ===")
propietarios = Propietario.objects.all()
for p in propietarios:
    print(f"\nPropietario: {p.user.get_full_name()}")
    print(f"  - Username: {p.user.username}")
    print(f"  - Documento: {p.documento_identidad}")
    print(f"  - Teléfono: {p.telefono}")

# Verificar contraseña de carlos
print("\n=== VERIFICANDO CONTRASEÑA DE CARLOS ===")
carlos = User.objects.get(username='carlos')
print(f"Password '82028877': {carlos.check_password('82028877')}")
print(f"Password '8202887': {carlos.check_password('8202887')}")
