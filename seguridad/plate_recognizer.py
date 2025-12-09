import requests
from django.conf import settings
from typing import Dict, Optional
import base64


class PlateRecognizerService:
    """
    Servicio para reconocimiento de placas vehiculares usando Plate Recognizer API
    https://platerecognizer.com/
    """
    
    def __init__(self):
        self.api_url = "https://api.platerecognizer.com/v1/plate-reader/"
        self.api_token = getattr(settings, 'PLATE_RECOGNIZER_API_KEY', None)
        
    def recognize_plate(self, image_file) -> Dict:
        """
        Reconoce la placa en una imagen usando Plate Recognizer API
        
        Args:
            image_file: Archivo de imagen (Django UploadedFile or file-like object)
            
        Returns:
            Dict con el resultado del reconocimiento
        """
        # Validar que la API key esté configurada
        if not self.api_token:
            return {
                'success': False,
                'error': 'PLATE_RECOGNIZER_API_KEY no está configurada en settings'
            }
        
        try:
            # Preparar headers
            headers = {
                'Authorization': f'Token {self.api_token}'
            }
            
            # Resetear el puntero del archivo al inicio
            image_file.seek(0)
            
            # Preparar el archivo para la petición
            files = {
                'upload': image_file
            }
            
            # Parámetros adicionales (opcional)
            data = {
                'regions': ['mx', 'us', 'br', 'ar'],  # Regiones a buscar
            }
            
            # Hacer la petición a la API
            response = requests.post(
                self.api_url,
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                return self._process_success_response(result)
            else:
                return {
                    'success': False,
                    'error': f'Error de API: {response.status_code}',
                    'details': response.text
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Timeout: La API tardó demasiado en responder'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }
    
    def _process_success_response(self, api_response: Dict) -> Dict:
        """
        Procesa la respuesta exitosa de la API
        
        Args:
            api_response: Respuesta JSON de la API
            
        Returns:
            Dict con datos procesados
        """
        results = api_response.get('results', [])
        
        if not results:
            return {
                'success': False,
                'error': 'No se detectó ninguna placa en la imagen'
            }
        
        # Tomar el resultado con mayor confianza
        best_result = max(results, key=lambda x: x.get('score', 0))
        
        plate_number = best_result.get('plate', '').upper()
        score = best_result.get('score', 0) * 100  # Convertir a porcentaje
        
        # Determinar nivel de confianza
        if score >= 85:
            confidence = 'high'
        elif score >= 70:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # Extraer información del vehículo
        vehicle_info = best_result.get('vehicle', {})
        
        return {
            'success': True,
            'plate_number': plate_number,
            'confidence': confidence,
            'confidence_score': round(score, 2),
            'region': best_result.get('region', {}).get('code', ''),
            'vehicle_type': vehicle_info.get('type', ''),
            'vehicle_make': self._get_vehicle_make(vehicle_info),
            'vehicle_model': self._get_vehicle_model(vehicle_info),
            'vehicle_color': self._get_vehicle_color(vehicle_info),
            'raw_response': api_response,
            'processing_time': api_response.get('processing_time', 0)
        }
    
    def _get_vehicle_make(self, vehicle_info: Dict) -> Optional[str]:
        """Extrae la marca del vehículo con mayor confianza"""
        makes = vehicle_info.get('make', [])
        if makes:
            return makes[0].get('name', '').title()
        return None
    
    def _get_vehicle_model(self, vehicle_info: Dict) -> Optional[str]:
        """Extrae el modelo del vehículo con mayor confianza"""
        models = vehicle_info.get('make_model', [])
        if models:
            return models[0].get('name', '').title()
        return None
    
    def _get_vehicle_color(self, vehicle_info: Dict) -> Optional[str]:
        """Extrae el color del vehículo con mayor confianza"""
        colors = vehicle_info.get('color', [])
        if colors:
            return colors[0].get('color', '').title()
        return None
    
    def batch_recognize(self, image_files: list) -> list:
        """
        Reconoce placas en múltiples imágenes
        
        Args:
            image_files: Lista de archivos de imagen
            
        Returns:
            Lista de resultados
        """
        results = []
        for image_file in image_files:
            result = self.recognize_plate(image_file)
            results.append(result)
        return results
