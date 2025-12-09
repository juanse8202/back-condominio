from rest_framework import serializers
from .models import Visita, RegistroVisita, Guardia, ComunicacionGuardia, PlateRecognitionLog
from gestion.models import Vehiculo


class VisitaSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(source='propietario.user.get_full_name', read_only=True)
    unidad = serializers.CharField(source='propietario.unidad.numero', read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Visita
        fields = ['id', 'propietario', 'propietario_nombre', 'unidad', 'nombre_visitante',
                  'documento_identidad', 'telefono', 'fecha_visita', 'hora_inicio', 'hora_fin',
                  'placa_vehiculo', 'codigo_acceso', 'qr_code', 'qr_code_url', 'estado', 'fecha_creacion']
        read_only_fields = ['codigo_acceso', 'qr_code', 'qr_code_url', 'fecha_creacion']
    
    def get_qr_code_url(self, obj):
        """Retorna la URL de ImgBB si está disponible, sino la URL local."""
        # Prioridad: URL de ImgBB > URL local
        if hasattr(obj, 'qr_code_url') and obj.qr_code_url:
            return obj.qr_code_url
        elif obj.qr_code:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code.url)
        return None


class RegistroVisitaSerializer(serializers.ModelSerializer):
    visita_detalle = serializers.SerializerMethodField()
    guardia_nombre = serializers.CharField(source='guardia.nombre', read_only=True)
    foto_entrada_url = serializers.SerializerMethodField()
    
    class Meta:
        model = RegistroVisita
        fields = ['id', 'visita', 'visita_detalle', 'guardia', 'guardia_nombre',
                  'hora_entrada', 'hora_salida', 'foto_entrada', 'foto_entrada_url', 'observaciones']
        read_only_fields = ['hora_entrada', 'foto_entrada_url']
    
    def get_visita_detalle(self, obj):
        return f"{obj.visita.nombre_visitante} - {obj.visita.propietario.unidad.numero}"
    
    def get_foto_entrada_url(self, obj):
        """Retorna la URL de ImgBB si está disponible, sino la URL local."""
        if hasattr(obj, 'foto_entrada_url') and obj.foto_entrada_url:
            return obj.foto_entrada_url
        elif obj.foto_entrada:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.foto_entrada.url)
        return None


class GuardiaSerializer(serializers.ModelSerializer):
    user_nombre = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Guardia
        fields = ['id', 'user', 'user_nombre', 'turno', 'telefono', 'activo']


class ComunicacionGuardiaSerializer(serializers.ModelSerializer):
    guardia_nombre = serializers.CharField(source='guardia.nombre', read_only=True)
    propietario_nombre = serializers.CharField(source='propietario.user.get_full_name', read_only=True)
    
    class Meta:
        model = ComunicacionGuardia
        fields = ['id', 'guardia', 'guardia_nombre', 'propietario', 'propietario_nombre',
                  'tipo', 'mensaje', 'fecha_comunicacion', 'leido']
        read_only_fields = ['fecha_comunicacion']


class PlateRecognitionLogSerializer(serializers.ModelSerializer):
    vehiculo_info = serializers.SerializerMethodField()
    unidad_info = serializers.SerializerMethodField()
    guardia_nombre = serializers.CharField(source='guardia.user.get_full_name', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PlateRecognitionLog
        fields = [
            'id', 'plate_number', 'plate_region', 'vehicle_type', 
            'vehicle_make', 'vehicle_model', 'vehicle_color',
            'image', 'image_url', 'confidence', 'confidence_score',
            'vehiculo', 'vehiculo_info', 'unidad', 'unidad_info',
            'visita', 'guardia', 'guardia_nombre',
            'is_registered', 'tipo_acceso', 'acceso_permitido', 
            'acceso_automatico', 'fecha_reconocimiento', 'observaciones'
        ]
        read_only_fields = ['fecha_reconocimiento', 'image_url']
    
    def get_image_url(self, obj):
        """Retorna la URL de ImgBB si está disponible, sino la URL local."""
        if hasattr(obj, 'image_url') and obj.image_url:
            return obj.image_url
        elif obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_vehiculo_info(self, obj):
        if obj.vehiculo:
            return {
                'id': obj.vehiculo.id,
                'placa': obj.vehiculo.placa,
                'marca': obj.vehiculo.marca,
                'modelo': obj.vehiculo.modelo,
                'color': obj.vehiculo.color,
                'propietario': obj.vehiculo.propietario.user.get_full_name(),
            }
        return None
    
    def get_unidad_info(self, obj):
        if obj.unidad:
            return {
                'id': obj.unidad.id,
                'numero': obj.unidad.numero,
                'tipo': obj.unidad.tipo,
                'propietario': obj.unidad.propietario.user.get_full_name(),
            }
        return None
