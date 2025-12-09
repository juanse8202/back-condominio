from rest_framework import serializers
from .models import Reporte


class ReporteSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.SerializerMethodField(read_only=True)
    unidad = serializers.CharField(source='propietario.unidad.numero', read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(source='fecha_reporte', read_only=True)
    
    class Meta:
        model = Reporte
        fields = ['id', 'propietario', 'propietario_nombre', 'unidad', 'tipo', 'estado',
                  'prioridad', 'titulo', 'descripcion', 'ubicacion', 'foto',
                  'fecha_reporte', 'created_at']
        read_only_fields = ['fecha_reporte', 'created_at']
    
    def get_propietario_nombre(self, obj):
        if obj.propietario and obj.propietario.user:
            full_name = obj.propietario.user.get_full_name()
            return full_name if full_name.strip() else obj.propietario.user.username
        return None
