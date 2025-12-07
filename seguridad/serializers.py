from rest_framework import serializers
from .models import Visita, RegistroVisita, Guardia, ComunicacionGuardia


class VisitaSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(source='propietario.user.get_full_name', read_only=True)
    unidad = serializers.CharField(source='propietario.unidad.numero', read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Visita
        fields = ['id', 'propietario', 'propietario_nombre', 'unidad', 'nombre_visitante',
                  'documento_identidad', 'telefono', 'fecha_visita', 'hora_inicio', 'hora_fin',
                  'placa_vehiculo', 'codigo_acceso', 'qr_code', 'qr_code_url', 'estado', 'fecha_creacion']
        read_only_fields = ['codigo_acceso', 'qr_code', 'fecha_creacion']
    
    def get_qr_code_url(self, obj):
        if obj.qr_code:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code.url)
        return None


class RegistroVisitaSerializer(serializers.ModelSerializer):
    visita_detalle = serializers.SerializerMethodField()
    guardia_nombre = serializers.CharField(source='guardia.nombre', read_only=True)
    
    class Meta:
        model = RegistroVisita
        fields = ['id', 'visita', 'visita_detalle', 'guardia', 'guardia_nombre',
                  'hora_entrada', 'hora_salida', 'observaciones']
        read_only_fields = ['hora_entrada']
    
    def get_visita_detalle(self, obj):
        return f"{obj.visita.nombre_visitante} - {obj.visita.propietario.unidad.numero}"


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
