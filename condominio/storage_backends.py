"""
Backends de almacenamiento personalizados para integrar ImgBB.
Permite que Django use ImgBB en lugar de almacenamiento local.
"""
from django.core.files.storage import Storage
from django.core.files.base import File
from django.utils.deconstruct import deconstructible
from .imgbb_service import imgbb_service
import logging

logger = logging.getLogger(__name__)


@deconstructible
class ImgBBStorage(Storage):
    """
    Storage backend personalizado para usar ImgBB como almacenamiento de imágenes.
    """
    
    def __init__(self, folder_type='general'):
        self.folder_type = folder_type
        self.base_url = "https://i.ibb.co/"
    
    def _open(self, name, mode='rb'):
        """
        No necesitamos abrir archivos desde ImgBB localmente.
        """
        raise NotImplementedError("ImgBBStorage no soporta lectura directa de archivos")
    
    def _save(self, name, content):
        """
        Guarda el archivo en ImgBB y retorna la URL.
        
        Args:
            name: Nombre del archivo
            content: Contenido del archivo (File object)
            
        Returns:
            URL de la imagen en ImgBB
        """
        try:
            result = imgbb_service.upload_image(
                image_file=content,
                folder_type=self.folder_type,
                name=name
            )
            
            if result and result.get('url'):
                logger.info(f"Imagen guardada en ImgBB: {result['url']}")
                # Retornamos la URL completa
                return result['url']
            else:
                logger.error(f"No se pudo guardar la imagen en ImgBB: {name}")
                raise IOError(f"No se pudo subir la imagen {name} a ImgBB")
                
        except Exception as e:
            logger.error(f"Error al guardar en ImgBB: {str(e)}")
            raise
    
    def delete(self, name):
        """
        Elimina un archivo de ImgBB.
        """
        # Como name es la URL, necesitamos el delete_url que no tenemos aquí
        # La eliminación se manejará manualmente si es necesario
        logger.warning(f"Eliminación de ImgBB debe hacerse manualmente: {name}")
    
    def exists(self, name):
        """
        ImgBB siempre crea URLs únicas, por lo que consideramos que no existe.
        """
        return False
    
    def url(self, name):
        """
        Retorna la URL del archivo.
        Si name ya es una URL completa, la retornamos tal cual.
        """
        if name.startswith('http'):
            return name
        return name
    
    def size(self, name):
        """
        No podemos obtener el tamaño desde ImgBB fácilmente.
        """
        return 0
    
    def get_available_name(self, name, max_length=None):
        """
        ImgBB maneja nombres únicos automáticamente.
        """
        return name


def get_imgbb_storage(folder_type):
    """
    Factory function para crear storage de ImgBB con un folder_type específico.
    
    Usage en models:
        foto = models.ImageField(storage=get_imgbb_storage('vehiculos'))
    """
    return ImgBBStorage(folder_type=folder_type)
