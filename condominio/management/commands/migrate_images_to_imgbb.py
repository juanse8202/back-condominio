"""
Utilidad para migrar imágenes existentes a ImgBB.
"""
from django.core.management.base import BaseCommand
from seguridad.models import Visita, RegistroVisita, PlateRecognitionLog
from administracion.models import PerfilUsuario
from gestion.models import Vehiculo, Mascota
from condominio.imgbb_service import imgbb_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migra todas las imágenes locales existentes a ImgBB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Modelo específico a migrar (visitas, registros, placas, usuarios, vehiculos, mascotas, all)',
            default='all'
        )

    def handle(self, *args, **options):
        model_choice = options['model']
        
        if model_choice in ['visitas', 'all']:
            self.migrar_qr_visitas()
        
        if model_choice in ['registros', 'all']:
            self.migrar_fotos_registros()
        
        if model_choice in ['placas', 'all']:
            self.migrar_imagenes_placas()
        
        if model_choice in ['usuarios', 'all']:
            self.migrar_fotos_usuarios()
        
        if model_choice in ['vehiculos', 'all']:
            self.migrar_fotos_vehiculos()
        
        if model_choice in ['mascotas', 'all']:
            self.migrar_fotos_mascotas()
        
        self.stdout.write(self.style.SUCCESS('Migración completada'))

    def migrar_qr_visitas(self):
        """Migra QR codes de visitas a ImgBB."""
        self.stdout.write('Migrando QR codes de visitas...')
        visitas = Visita.objects.filter(qr_code__isnull=False, qr_code_url__isnull=True)
        
        total = visitas.count()
        migrados = 0
        
        for visita in visitas:
            try:
                result = imgbb_service.upload_image(
                    image_file=visita.qr_code,
                    folder_type='qrcodes_visitas',
                    name=f'qr_visita_{visita.codigo_acceso}'
                )
                
                if result:
                    visita.qr_code_url = result['url']
                    visita.qr_code_delete_url = result['delete_url']
                    visita.save(update_fields=['qr_code_url', 'qr_code_delete_url'])
                    migrados += 1
                    self.stdout.write(f'✓ Visita {visita.id} migrada')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error en visita {visita.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'QR Visitas: {migrados}/{total} migrados'))

    def migrar_fotos_registros(self):
        """Migra fotos de registros de visitas a ImgBB."""
        self.stdout.write('Migrando fotos de registros...')
        registros = RegistroVisita.objects.filter(foto_entrada__isnull=False, foto_entrada_url__isnull=True)
        
        total = registros.count()
        migrados = 0
        
        for registro in registros:
            try:
                result = imgbb_service.upload_image(
                    image_file=registro.foto_entrada,
                    folder_type='fotos_visitas',
                    name=f'foto_visita_{registro.visita.codigo_acceso}_{registro.id}'
                )
                
                if result:
                    registro.foto_entrada_url = result['url']
                    registro.foto_entrada_delete_url = result['delete_url']
                    registro.save(update_fields=['foto_entrada_url', 'foto_entrada_delete_url'])
                    migrados += 1
                    self.stdout.write(f'✓ Registro {registro.id} migrado')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error en registro {registro.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Fotos Registros: {migrados}/{total} migrados'))

    def migrar_imagenes_placas(self):
        """Migra imágenes de reconocimiento de placas a ImgBB."""
        self.stdout.write('Migrando imágenes de placas...')
        logs = PlateRecognitionLog.objects.filter(image__isnull=False, image_url__isnull=True)
        
        total = logs.count()
        migrados = 0
        
        for log in logs:
            try:
                result = imgbb_service.upload_image(
                    image_file=log.image,
                    folder_type='plate_recognition',
                    name=f'plate_{log.plate_number}_{log.id}'
                )
                
                if result:
                    log.image_url = result['url']
                    log.image_delete_url = result['delete_url']
                    log.save(update_fields=['image_url', 'image_delete_url'])
                    migrados += 1
                    self.stdout.write(f'✓ Placa {log.id} migrada')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error en placa {log.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imágenes Placas: {migrados}/{total} migrados'))

    def migrar_fotos_usuarios(self):
        """Migra fotos de perfiles de usuarios a ImgBB."""
        self.stdout.write('Migrando fotos de usuarios...')
        perfiles = PerfilUsuario.objects.filter(foto__isnull=False, foto_url__isnull=True)
        
        total = perfiles.count()
        migrados = 0
        
        for perfil in perfiles:
            try:
                result = imgbb_service.upload_image(
                    image_file=perfil.foto,
                    folder_type='usuarios/fotos',
                    name=f'usuario_{perfil.user.username}_{perfil.id}'
                )
                
                if result:
                    perfil.foto_url = result['url']
                    perfil.foto_delete_url = result['delete_url']
                    perfil.save(update_fields=['foto_url', 'foto_delete_url'])
                    migrados += 1
                    self.stdout.write(f'✓ Usuario {perfil.id} migrado')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error en usuario {perfil.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Fotos Usuarios: {migrados}/{total} migrados'))

    def migrar_fotos_vehiculos(self):
        """Migra fotos de vehículos a ImgBB."""
        self.stdout.write('Migrando fotos de vehículos...')
        vehiculos = Vehiculo.objects.filter(foto_vehiculo__isnull=False, foto_vehiculo_url__isnull=True)
        
        total = vehiculos.count()
        migrados = 0
        
        for vehiculo in vehiculos:
            try:
                result = imgbb_service.upload_image(
                    image_file=vehiculo.foto_vehiculo,
                    folder_type='vehiculos',
                    name=f'vehiculo_{vehiculo.placa}_{vehiculo.id}'
                )
                
                if result:
                    vehiculo.foto_vehiculo_url = result['url']
                    vehiculo.foto_vehiculo_delete_url = result['delete_url']
                    vehiculo.save(update_fields=['foto_vehiculo_url', 'foto_vehiculo_delete_url'])
                    migrados += 1
                    self.stdout.write(f'✓ Vehículo {vehiculo.id} migrado')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error en vehículo {vehiculo.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Fotos Vehículos: {migrados}/{total} migrados'))

    def migrar_fotos_mascotas(self):
        """Migra fotos de mascotas a ImgBB."""
        self.stdout.write('Migrando fotos de mascotas...')
        mascotas = Mascota.objects.filter(foto__isnull=False, foto_url__isnull=True)
        
        total = mascotas.count()
        migrados = 0
        
        for mascota in mascotas:
            try:
                result = imgbb_service.upload_image(
                    image_file=mascota.foto,
                    folder_type='mascotas',
                    name=f'mascota_{mascota.nombre}_{mascota.id}'
                )
                
                if result:
                    mascota.foto_url = result['url']
                    mascota.foto_delete_url = result['delete_url']
                    mascota.save(update_fields=['foto_url', 'foto_delete_url'])
                    migrados += 1
                    self.stdout.write(f'✓ Mascota {mascota.id} migrada')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error en mascota {mascota.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Fotos Mascotas: {migrados}/{total} migrados'))
