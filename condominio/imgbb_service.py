"""
Servicio de integración con ImgBB para almacenar imágenes en la nube.
Organiza las imágenes en diferentes álbumes/carpetas según su tipo.
"""
import base64
import requests
from django.conf import settings
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class ImgBBService:
    """
    Servicio para subir imágenes a ImgBB de forma automática.
    Las imágenes se organizan por carpetas/álbumes según su tipo.
    """
    
    API_URL = "https://api.imgbb.com/1/upload"
    
    # Configuración de carpetas/álbumes para diferentes tipos de imágenes
    FOLDERS = {
        'qrcodes_visitas': 'condominio_qr_visitas',
        'fotos_visitas': 'condominio_fotos_visitas',
        'plate_recognition': 'condominio_reconocimiento_placas',
        'usuarios/fotos': 'condominio_usuarios',
        'vehiculos': 'condominio_vehiculos',
        'mascotas': 'condominio_mascotas',
    }
    
    def __init__(self):
        self.api_key = getattr(settings, 'IMGBB_API_KEY', None)
        if not self.api_key:
            logger.warning("IMGBB_API_KEY no configurada en settings")
    
    def upload_image(
        self, 
        image_file, 
        folder_type: str, 
        name: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Sube una imagen a ImgBB.
        
        Args:
            image_file: Archivo de imagen (File object o path)
            folder_type: Tipo de carpeta (debe estar en FOLDERS)
            name: Nombre opcional para la imagen
            
        Returns:
            Dict con información de la imagen subida o None si falla
            {
                'url': 'https://...',
                'delete_url': 'https://...',
                'thumb_url': 'https://...',
                'medium_url': 'https://...',
                'display_url': 'https://...',
                'size': 12345,
                'title': 'nombre'
            }
        """
        if not self.api_key:
            logger.error("No se puede subir imagen: IMGBB_API_KEY no configurada")
            return None
        
        try:
            # Leer el archivo y convertirlo a base64
            if hasattr(image_file, 'read'):
                image_file.seek(0)
                image_data = image_file.read()
            else:
                with open(image_file, 'rb') as f:
                    image_data = f.read()
            
            # Convertir a base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Preparar datos para la API
            album_name = self.FOLDERS.get(folder_type, 'condominio_general')
            
            data = {
                'key': self.api_key,
                'image': image_base64,
                'name': name or f"{album_name}_{hash(image_data)}",
            }
            
            # Realizar la petición
            response = requests.post(self.API_URL, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success'):
                image_info = result['data']
                logger.info(f"Imagen subida exitosamente a ImgBB: {image_info.get('url')}")
                
                return {
                    'url': image_info.get('url'),
                    'delete_url': image_info.get('delete_url'),
                    'thumb_url': image_info.get('thumb', {}).get('url'),
                    'medium_url': image_info.get('medium', {}).get('url'),
                    'display_url': image_info.get('display_url'),
                    'size': image_info.get('size'),
                    'title': image_info.get('title'),
                    'delete_hash': image_info.get('delete_url', '').split('/')[-1] if image_info.get('delete_url') else None,
                }
            else:
                logger.error(f"Error al subir imagen a ImgBB: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con ImgBB: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al subir imagen: {str(e)}")
            return None
    
    def delete_image(self, delete_url: str) -> bool:
        """
        Elimina una imagen de ImgBB usando su delete_url.
        
        Args:
            delete_url: URL de eliminación proporcionada por ImgBB
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        try:
            response = requests.get(delete_url, timeout=10)
            response.raise_for_status()
            logger.info(f"Imagen eliminada de ImgBB: {delete_url}")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar imagen de ImgBB: {str(e)}")
            return False
    
    @staticmethod
    def get_folder_type_from_upload_path(upload_path: str) -> str:
        """
        Determina el tipo de carpeta basado en el upload_to del modelo.
        
        Args:
            upload_path: Ruta de upload_to (ej: 'qrcodes_visitas/')
            
        Returns:
            Tipo de carpeta para FOLDERS
        """
        upload_path = upload_path.strip('/')
        return upload_path


# Instancia global del servicio
imgbb_service = ImgBBService()
