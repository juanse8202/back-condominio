from rest_framework import serializers
from .models import Comunicado


class ComunicadoSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.CharField(source='autor.get_full_name', read_only=True)
    
    class Meta:
        model = Comunicado
        fields = ['id', 'titulo', 'contenido', 'tipo', 'prioridad', 'autor', 'autor_nombre',
                  'fecha_publicacion', 'fecha_evento', 'imagen', 'activo']
        read_only_fields = ['fecha_publicacion', 'autor']
    
    def create(self, validated_data):
        # El autor se asigna desde la vista con el usuario actual
        return super().create(validated_data)
