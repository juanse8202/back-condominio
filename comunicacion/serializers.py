from rest_framework import serializers
from .models import Comunicado


class ComunicadoSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Comunicado
        fields = ['id', 'titulo', 'contenido', 'tipo', 'prioridad', 'autor', 'autor_nombre',
                  'fecha_publicacion', 'imagen', 'activo']
        read_only_fields = ['fecha_publicacion', 'autor']
    
    def get_autor_nombre(self, obj):
        if obj.autor:
            full_name = obj.autor.get_full_name()
            return full_name if full_name.strip() else obj.autor.username
        return None
    
    def create(self, validated_data):
        # El autor se asigna desde la vista con el usuario actual
        return super().create(validated_data)
