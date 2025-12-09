"""
Signals para subir automáticamente imágenes a ImgBB cuando se guardan modelos.
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Visita, RegistroVisita, PlateRecognitionLog
from administracion.models import PerfilUsuario
from gestion.models import Vehiculo, Mascota
from condominio.imgbb_service import imgbb_service
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Visita)
def subir_qr_visita_a_imgbb(sender, instance, created, **kwargs):
    """
    Sube el QR code de la visita a ImgBB automáticamente.
    """
    # Solo procesar si tiene QR code y no tiene URL todavía
    if instance.qr_code and not instance.qr_code_url:
        try:
            result = imgbb_service.upload_image(
                image_file=instance.qr_code,
                folder_type='qrcodes_visitas',
                name=f'qr_visita_{instance.codigo_acceso}'
            )
            
            if result:
                # Actualizar URLs sin disparar el signal nuevamente
                Visita.objects.filter(pk=instance.pk).update(
                    qr_code_url=result['url'],
                    qr_code_delete_url=result['delete_url']
                )
                logger.info(f"QR de visita {instance.id} subido a ImgBB: {result['url']}")
        except Exception as e:
            logger.error(f"Error al subir QR de visita a ImgBB: {str(e)}")


@receiver(post_save, sender=RegistroVisita)
def subir_foto_visita_a_imgbb(sender, instance, created, **kwargs):
    """
    Sube la foto de entrada de la visita a ImgBB automáticamente.
    """
    if instance.foto_entrada and not instance.foto_entrada_url:
        try:
            result = imgbb_service.upload_image(
                image_file=instance.foto_entrada,
                folder_type='fotos_visitas',
                name=f'foto_visita_{instance.visita.codigo_acceso}_{instance.id}'
            )
            
            if result:
                RegistroVisita.objects.filter(pk=instance.pk).update(
                    foto_entrada_url=result['url'],
                    foto_entrada_delete_url=result['delete_url']
                )
                logger.info(f"Foto de visita {instance.id} subida a ImgBB: {result['url']}")
        except Exception as e:
            logger.error(f"Error al subir foto de visita a ImgBB: {str(e)}")


@receiver(post_save, sender=PlateRecognitionLog)
def subir_imagen_placa_a_imgbb(sender, instance, created, **kwargs):
    """
    Sube la imagen de reconocimiento de placa a ImgBB automáticamente.
    """
    if instance.image and not instance.image_url:
        try:
            result = imgbb_service.upload_image(
                image_file=instance.image,
                folder_type='plate_recognition',
                name=f'plate_{instance.plate_number}_{instance.id}'
            )
            
            if result:
                PlateRecognitionLog.objects.filter(pk=instance.pk).update(
                    image_url=result['url'],
                    image_delete_url=result['delete_url']
                )
                logger.info(f"Imagen de placa {instance.id} subida a ImgBB: {result['url']}")
        except Exception as e:
            logger.error(f"Error al subir imagen de placa a ImgBB: {str(e)}")


@receiver(post_save, sender=PerfilUsuario)
def subir_foto_usuario_a_imgbb(sender, instance, created, **kwargs):
    """
    Sube la foto del usuario a ImgBB automáticamente.
    """
    if instance.foto and not instance.foto_url:
        try:
            result = imgbb_service.upload_image(
                image_file=instance.foto,
                folder_type='usuarios/fotos',
                name=f'usuario_{instance.user.username}_{instance.id}'
            )
            
            if result:
                PerfilUsuario.objects.filter(pk=instance.pk).update(
                    foto_url=result['url'],
                    foto_delete_url=result['delete_url']
                )
                logger.info(f"Foto de usuario {instance.id} subida a ImgBB: {result['url']}")
        except Exception as e:
            logger.error(f"Error al subir foto de usuario a ImgBB: {str(e)}")


@receiver(post_save, sender=Vehiculo)
def subir_foto_vehiculo_a_imgbb(sender, instance, created, **kwargs):
    """
    Sube la foto del vehículo a ImgBB automáticamente.
    """
    if instance.foto_vehiculo and not instance.foto_vehiculo_url:
        try:
            result = imgbb_service.upload_image(
                image_file=instance.foto_vehiculo,
                folder_type='vehiculos',
                name=f'vehiculo_{instance.placa}_{instance.id}'
            )
            
            if result:
                Vehiculo.objects.filter(pk=instance.pk).update(
                    foto_vehiculo_url=result['url'],
                    foto_vehiculo_delete_url=result['delete_url']
                )
                logger.info(f"Foto de vehículo {instance.id} subida a ImgBB: {result['url']}")
        except Exception as e:
            logger.error(f"Error al subir foto de vehículo a ImgBB: {str(e)}")


@receiver(post_save, sender=Mascota)
def subir_foto_mascota_a_imgbb(sender, instance, created, **kwargs):
    """
    Sube la foto de la mascota a ImgBB automáticamente.
    """
    if instance.foto and not instance.foto_url:
        try:
            result = imgbb_service.upload_image(
                image_file=instance.foto,
                folder_type='mascotas',
                name=f'mascota_{instance.nombre}_{instance.id}'
            )
            
            if result:
                Mascota.objects.filter(pk=instance.pk).update(
                    foto_url=result['url'],
                    foto_delete_url=result['delete_url']
                )
                logger.info(f"Foto de mascota {instance.id} subida a ImgBB: {result['url']}")
        except Exception as e:
            logger.error(f"Error al subir foto de mascota a ImgBB: {str(e)}")


# Signals para eliminar imágenes de ImgBB cuando se elimina el registro
@receiver(pre_delete, sender=Visita)
def eliminar_qr_visita_de_imgbb(sender, instance, **kwargs):
    """Elimina el QR de ImgBB al eliminar la visita."""
    if instance.qr_code_delete_url:
        try:
            imgbb_service.delete_image(instance.qr_code_delete_url)
        except Exception as e:
            logger.error(f"Error al eliminar QR de ImgBB: {str(e)}")


@receiver(pre_delete, sender=RegistroVisita)
def eliminar_foto_visita_de_imgbb(sender, instance, **kwargs):
    """Elimina la foto de ImgBB al eliminar el registro de visita."""
    if instance.foto_entrada_delete_url:
        try:
            imgbb_service.delete_image(instance.foto_entrada_delete_url)
        except Exception as e:
            logger.error(f"Error al eliminar foto de visita de ImgBB: {str(e)}")


@receiver(pre_delete, sender=PlateRecognitionLog)
def eliminar_imagen_placa_de_imgbb(sender, instance, **kwargs):
    """Elimina la imagen de ImgBB al eliminar el log de reconocimiento."""
    if instance.image_delete_url:
        try:
            imgbb_service.delete_image(instance.image_delete_url)
        except Exception as e:
            logger.error(f"Error al eliminar imagen de placa de ImgBB: {str(e)}")


@receiver(pre_delete, sender=PerfilUsuario)
def eliminar_foto_usuario_de_imgbb(sender, instance, **kwargs):
    """Elimina la foto de ImgBB al eliminar el perfil de usuario."""
    if instance.foto_delete_url:
        try:
            imgbb_service.delete_image(instance.foto_delete_url)
        except Exception as e:
            logger.error(f"Error al eliminar foto de usuario de ImgBB: {str(e)}")


@receiver(pre_delete, sender=Vehiculo)
def eliminar_foto_vehiculo_de_imgbb(sender, instance, **kwargs):
    """Elimina la foto de ImgBB al eliminar el vehículo."""
    if instance.foto_vehiculo_delete_url:
        try:
            imgbb_service.delete_image(instance.foto_vehiculo_delete_url)
        except Exception as e:
            logger.error(f"Error al eliminar foto de vehículo de ImgBB: {str(e)}")


@receiver(pre_delete, sender=Mascota)
def eliminar_foto_mascota_de_imgbb(sender, instance, **kwargs):
    """Elimina la foto de ImgBB al eliminar la mascota."""
    if instance.foto_delete_url:
        try:
            imgbb_service.delete_image(instance.foto_delete_url)
        except Exception as e:
            logger.error(f"Error al eliminar foto de mascota de ImgBB: {str(e)}")
