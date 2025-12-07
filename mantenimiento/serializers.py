from rest_framework import serializers
from .models import Reporte


class ReporteSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(source='propietario.user.get_full_name', read_only=True)
    unidad = serializers.CharField(source='propietario.unidad.numero', read_only=True)
    
    class Meta:
        model = Reporte
        fields = ['id', 'propietario', 'propietario_nombre', 'unidad', 'tipo', 'estado',
                  'prioridad', 'titulo', 'descripcion', 'ubicacion', 'imagen',
                  'fecha_reporte', 'fecha_resolucion']
        read_only_fields = ['fecha_reporte', 'fecha_resolucion']
