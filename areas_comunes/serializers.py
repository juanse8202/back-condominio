from rest_framework import serializers
from .models import AreaComun, ReservaAreaComun


class AreaComunSerializer(serializers.ModelSerializer):
    disponible = serializers.SerializerMethodField()
    
    class Meta:
        model = AreaComun
        fields = ['id', 'nombre', 'descripcion', 'capacidad', 'horario_apertura', 
                  'horario_cierre', 'tarifa_hora', 'tipo_cobro', 'activa', 'disponible']
    
    def get_disponible(self, obj):
        return obj.activa


class ReservaAreaComunSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(source='propietario.user.get_full_name', read_only=True)
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)
    unidad = serializers.CharField(source='propietario.unidad.numero', read_only=True)
    
    class Meta:
        model = ReservaAreaComun
        fields = ['id', 'propietario', 'propietario_nombre', 'unidad', 'area', 'area_nombre',
                  'fecha', 'hora_inicio', 'hora_fin', 'num_personas', 'costo_total', 'estado', 
                  'codigo_reserva', 'fecha_reserva']
        read_only_fields = ['codigo_reserva', 'fecha_reserva', 'costo_total']
