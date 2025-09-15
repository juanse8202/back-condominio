# core/management/commands/populate_data.py
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    Propietario, UnidadHabitacional, Vehiculo, Mascota, 
    Reporte, Visita, AreaComun, ReservaAreaComun, 
    Expensa, Pago, Guardia, ComunicacionGuardia
)

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba'

    def handle(self, *args, **options):
        self.stdout.write('🧹 Limpiando datos existentes...')
        self.clean_database()
        
        self.stdout.write('👥 Creando usuarios y propietarios...')
        self.create_users_and_propietarios()
        
        self.stdout.write('🏠 Creando unidades habitacionales...')
        self.create_unidades_habitacionales()
        
        self.stdout.write('🚗 Creando vehículos...')
        self.create_vehiculos()
        
        self.stdout.write('🐾 Creando mascotas...')
        self.create_mascotas()
        
        self.stdout.write('📋 Creando reportes...')
        self.create_reportes()
        
        self.stdout.write('👥 Creando visitas...')
        self.create_visitas()
        
        self.stdout.write('🏊 Creando áreas comunes...')
        self.create_areas_comunes()
        
        self.stdout.write('📅 Creando reservas...')
        self.create_reservas()
        
        self.stdout.write('💰 Creando expensas...')
        self.create_expensas()
        
        self.stdout.write('💳 Creando pagos...')
        self.create_pagos()
        
        self.stdout.write('👮 Creando guardias...')
        self.create_guardias()
        
        self.stdout.write('📞 Creando comunicaciones...')
        self.create_comunicaciones()
        
        self.stdout.write('✅ ¡Base de datos poblada exitosamente!')

    def clean_database(self):
        # Limpiar en orden inverso para evitar problemas de foreign key
        ComunicacionGuardia.objects.all().delete()
        Guardia.objects.all().delete()
        Pago.objects.all().delete()
        Expensa.objects.all().delete()
        ReservaAreaComun.objects.all().delete()
        AreaComun.objects.all().delete()
        Visita.objects.all().delete()
        Reporte.objects.all().delete()
        Mascota.objects.all().delete()
        Vehiculo.objects.all().delete()
        UnidadHabitacional.objects.all().delete()
        Propietario.objects.all().delete()
        # No borramos usuarios por si acaso hay superusuarios

    def create_users_and_propietarios(self):
        users_data = [
            {'username': 'jperez', 'first_name': 'Juan', 'last_name': 'Pérez', 'email': 'juan@email.com'},
            {'username': 'mgonzalez', 'first_name': 'María', 'last_name': 'González', 'email': 'maria@email.com'},
            {'username': 'crodriguez', 'first_name': 'Carlos', 'last_name': 'Rodríguez', 'email': 'carlos@email.com'},
            {'username': 'alopez', 'first_name': 'Ana', 'last_name': 'López', 'email': 'ana@email.com'},
            {'username': 'pmartinez', 'first_name': 'Pedro', 'last_name': 'Martínez', 'email': 'pedro@email.com'},
            {'username': 'lhernandez', 'first_name': 'Laura', 'last_name': 'Hernández', 'email': 'laura@email.com'},
            {'username': 'jdiaz', 'first_name': 'José', 'last_name': 'Díaz', 'email': 'jose@email.com'},
            {'username': 'mruiz', 'first_name': 'Marta', 'last_name': 'Ruiz', 'email': 'marta@email.com'},
            {'username': 'fsanchez', 'first_name': 'Francisco', 'last_name': 'Sánchez', 'email': 'francisco@email.com'},
            {'username': 'egarcia', 'first_name': 'Elena', 'last_name': 'García', 'email': 'elena@email.com'},
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                    'password': 'password123'  # Contraseña simple para testing
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()

            # Crear propietario asociado
            documento = f"{random.randint(1000000, 9999999)}"
            telefono = f"7{random.randint(1000000, 9999999)}"
            
            Propietario.objects.get_or_create(
                user=user,
                defaults={
                    'documento_identidad': documento,
                    'telefono': telefono
                }
            )

    def create_unidades_habitacionales(self):
        edificios = ['Torre A', 'Torre B', 'Torre C', 'Torre D']
        tipos = ['casa', 'departamento', 'penthouse']
        
        propietarios = list(Propietario.objects.all())
        
        for i, propietario in enumerate(propietarios):
            unidad_data = {
                'numero': f"{i+1}{chr(65 + i % 4)}",  # 1A, 2B, 3C, etc.
                'edificio': random.choice(edificios),
                'tipo': random.choice(tipos),
                'piso': random.randint(1, 20) if random.choice(tipos) != 'casa' else None,
                'caracteristicas': f"Unidad {random.choice(['estándar', 'premium', 'vip'])} con {random.randint(2, 5)} habitaciones"
            }
            
            UnidadHabitacional.objects.get_or_create(
                propietario=propietario,
                defaults=unidad_data
            )

    def create_vehiculos(self):
        marcas = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'Hyundai', 'Kia', 'Volkswagen']
        modelos = {
            'Toyota': ['Corolla', 'Camry', 'RAV4', 'Hilux'],
            'Honda': ['Civic', 'Accord', 'CR-V', 'HR-V'],
            'Ford': ['Fiesta', 'Focus', 'Escape', 'Ranger'],
            'Chevrolet': ['Spark', 'Aveo', 'Cruze', 'Tracker'],
            'Nissan': ['Versa', 'Sentra', 'Qashqai', 'X-Trail'],
            'Hyundai': ['Accent', 'Elantra', 'Tucson', 'Santa Fe'],
            'Kia': ['Rio', 'Cerato', 'Sportage', 'Sorento'],
            'Volkswagen': ['Gol', 'Vento', 'Tiguan', 'Amarok']
        }
        colores = ['Rojo', 'Azul', 'Negro', 'Blanco', 'Gris', 'Plateado', 'Verde']
        
        for propietario in Propietario.objects.all():
            if random.random() > 0.3:  # 70% de probabilidad de tener vehículo
                marca = random.choice(marcas)
                Vehiculo.objects.create(
                    propietario=propietario,
                    placa=f"{random.randint(1000, 9999)}{chr(65 + random.randint(0, 25))}{chr(65 + random.randint(0, 25))}",
                    marca=marca,
                    modelo=random.choice(modelos[marca]),
                    color=random.choice(colores)
                )

    def create_mascotas(self):
        tipos_mascotas = ['perro', 'gato', 'ave', 'otro']
        razas_perros = ['Labrador', 'Pastor Alemán', 'Bulldog', 'Chihuahua', 'Poodle']
        razas_gatos = ['Siamés', 'Persa', 'Bengalí', 'Maine Coon', 'Esfinge']
        
        for propietario in Propietario.objects.all():
            if random.random() > 0.4:  # 60% de probabilidad de tener mascota
                tipo = random.choice(tipos_mascotas)
                Mascota.objects.create(
                    propietario=propietario,
                    nombre=random.choice(['Max', 'Luna', 'Bella', 'Rocky', 'Coco', 'Milo', 'Lola', 'Bruno']),
                    tipo=tipo,
                    raza=random.choice(razas_perros if tipo == 'perro' else razas_gatos if tipo == 'gato' else [''])
                )

    def create_reportes(self):
        tipos_reporte = ['incumplimiento', 'mantenimiento', 'seguridad', 'ruido', 'limpieza', 'otro']
        estados_reporte = ['pendiente', 'en_proceso', 'resuelto', 'rechazado']
        ubicaciones = ['Piscina', 'Estacionamiento', 'Área común', 'Ascensor', 'Jardín', 'Hall principal']
        
        for propietario in Propietario.objects.all():
            for _ in range(random.randint(0, 3)):  # 0-3 reportes por propietario
                Reporte.objects.create(
                    propietario=propietario,
                    tipo=random.choice(tipos_reporte),
                    titulo=f"Reporte de {random.choice(['problema', 'incidente', 'situación'])} en {random.choice(ubicaciones)}",
                    descripcion=f"Descripción detallada del problema reportado por el propietario. Situación ocurrida el {datetime.now().strftime('%d/%m/%Y')}",
                    ubicacion=random.choice(ubicaciones),
                    estado=random.choice(estados_reporte),
                    prioridad=random.randint(1, 5)
                )

    def create_visitas(self):
        for propietario in Propietario.objects.all():
            for _ in range(random.randint(1, 4)):  # 1-4 visitas por propietario
                fecha_visita = datetime.now() + timedelta(days=random.randint(-30, 30))
                Visita.objects.create(
                    propietario=propietario,
                    nombre_visitante=f"{random.choice(['Juan', 'María', 'Carlos', 'Ana', 'Pedro'])} {random.choice(['Pérez', 'González', 'Rodríguez', 'López', 'Martínez'])}",
                    documento_identidad=f"{random.randint(100000, 999999)}",
                    telefono=f"7{random.randint(100000, 999999)}",
                    fecha_visita=fecha_visita.date(),
                    hora_inicio=(datetime.now() + timedelta(hours=random.randint(9, 18))).time(),
                    hora_fin=(datetime.now() + timedelta(hours=random.randint(19, 22))).time(),
                    estado=random.choice(['programada', 'en_progreso', 'finalizada', 'cancelada'])
                )

    def create_areas_comunes(self):
        areas_data = [
            {'nombre': 'Piscina', 'capacidad': 20, 'tarifa_hora': 50.00},
            {'nombre': 'Salón de Eventos', 'capacidad': 50, 'tarifa_hora': 100.00},
            {'nombre': 'Cancha de Tenis', 'capacidad': 4, 'tarifa_hora': 30.00},
            {'nombre': 'Gimnasio', 'capacidad': 10, 'tarifa_hora': 25.00},
            {'nombre': 'Sala de Juegos', 'capacidad': 15, 'tarifa_hora': 40.00},
        ]
        
        for area_data in areas_data:
            AreaComun.objects.get_or_create(
                nombre=area_data['nombre'],
                defaults={
                    'descripcion': f"{area_data['nombre']} del condominio",
                    'capacidad': area_data['capacidad'],
                    'horario_apertura': '08:00:00',
                    'horario_cierre': '22:00:00',
                    'tarifa_hora': area_data['tarifa_hora']
                }
            )

    def create_reservas(self):
        areas = list(AreaComun.objects.all())
        propietarios = list(Propietario.objects.all())
        
        for _ in range(20):  # Crear 20 reservas
            area = random.choice(areas)
            propietario = random.choice(propietarios)
            fecha = datetime.now() + timedelta(days=random.randint(1, 60))
            
            horas_reserva = random.randint(1, 4)
            hora_inicio = random.randint(9, 19)
            
            ReservaAreaComun.objects.create(
                propietario=propietario,
                area=area,
                fecha=fecha.date(),
                hora_inicio=f"{hora_inicio:02d}:00:00",
                hora_fin=f"{hora_inicio + horas_reserva:02d}:00:00",
                costo_total=area.tarifa_hora * horas_reserva,
                estado=random.choice(['pendiente', 'confirmada', 'cancelada', 'completada'])
            )

    def create_expensas(self):
        meses = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05']
        
        for propietario in Propietario.objects.all():
            for mes in meses:
                cuota_basica = random.randint(500, 1000)
                multas = random.randint(0, 200) if random.random() > 0.7 else 0  # 30% de probabilidad de multa
                reservas = random.randint(0, 300)
                otros = random.randint(0, 100)
                
                Expensa.objects.create(
                    propietario=propietario,
                    mes_referencia=mes,
                    monto_total=cuota_basica + multas + reservas + otros,
                    cuota_basica=cuota_basica,
                    multas=multas,
                    reservas=reservas,
                    otros=otros,
                    fecha_vencimiento=datetime.now() + timedelta(days=random.randint(5, 15)),
                    pagada=random.random() > 0.4  # 60% de probabilidad de estar pagada
                )

    def create_pagos(self):
        metodos_pago = ['tarjeta', 'transferencia', 'efectivo']
        
        for expensa in Expensa.objects.filter(pagada=True):
            Pago.objects.create(
                expensa=expensa,
                monto=expensa.monto_total,
                metodo_pago=random.choice(metodos_pago),
                referencia=f"PAGO{random.randint(100000, 999999)}"
            )

    def create_guardias(self):
        guardias_data = [
            {'username': 'guardia1', 'first_name': 'Roberto', 'last_name': 'Silva', 'turno': 'Matutino'},
            {'username': 'guardia2', 'first_name': 'Miguel', 'last_name': 'Rojas', 'turno': 'Vespertino'},
            {'username': 'guardia3', 'first_name': 'Jorge', 'last_name': 'Mendoza', 'turno': 'Nocturno'},
        ]
        
        for guardia_data in guardias_data:
            user, created = User.objects.get_or_create(
                username=guardia_data['username'],
                defaults={
                    'first_name': guardia_data['first_name'],
                    'last_name': guardia_data['last_name'],
                    'password': 'guardia123'
                }
            )
            
            if created:
                user.set_password('guardia123')
                user.save()

            Guardia.objects.get_or_create(
                user=user,
                defaults={
                    'documento_identidad': f"{random.randint(1000000, 9999999)}",
                    'telefono': f"7{random.randint(1000000, 9999999)}",
                    'turno': guardia_data['turno'],
                    'fecha_contratacion': datetime.now() - timedelta(days=random.randint(100, 500))
                }
            )

    def create_comunicaciones(self):
        tipos_comunicacion = ['llamada', 'chat', 'asistencia', 'emergencia']
        estados_comunicacion = ['pendiente', 'en_proceso', 'atendida']
        
        propietarios = list(Propietario.objects.all())
        guardias = list(Guardia.objects.all())
        
        for _ in range(15):  # Crear 15 comunicaciones
            ComunicacionGuardia.objects.create(
                propietario=random.choice(propietarios),
                guardia=random.choice(guardias),
                tipo=random.choice(tipos_comunicacion),
                mensaje=random.choice([
                    "Problema con el acceso principal",
                    "Ruido excesivo en el piso 3",
                    "Visitante no autorizado",
                    "Fuga de agua en el pasillo",
                    "Luz quemada en el estacionamiento"
                ]),
                estado=random.choice(estados_comunicacion),
                respuesta=random.choice([
                    "Situación atendida",
                    "En proceso de resolución",
                    "Derivado a mantenimiento",
                    "Comunicado con el propietario"
                ]) if random.random() > 0.3 else ""  # 70% con respuesta
            )