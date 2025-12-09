from django.contrib.auth.models import User
from gestion.models import Propietario
from areas_comunes.models import ReservaAreaComun

print("=" * 50)
print("VERIFICACIÓN DE DATOS")
print("=" * 50)

# Propietarios
print(f"\nTotal propietarios: {Propietario.objects.count()}")
for p in Propietario.objects.all()[:3]:
    user_info = f"{p.user.username}" if p.user else "Sin usuario"
    print(f"  - {user_info} (propietario_id: {p.id})")

# Reservas
print(f"\nTotal reservas: {ReservaAreaComun.objects.count()}")
for r in ReservaAreaComun.objects.all()[:3]:
    print(f"  - {r.area.nombre} | {r.propietario.user.username} (prop_id: {r.propietario.id}) | {r.fecha} | Bs {r.costo_total}")

print("\n" + "=" * 50)
