from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Propietario, UnidadHabitacional, Vehiculo, Mascota


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class PropietarioSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Propietario
        fields = ['id', 'user', 'documento_identidad', 'telefono', 'fecha_registro', 
                  'nombre_completo', 'email', 'first_name', 'last_name', 'username',
                  'meses_mora', 'restringido_por_mora']
        read_only_fields = ['fecha_registro']
    
    def get_nombre_completo(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    def create(self, validated_data):
        # Extraer datos del usuario
        email = validated_data.pop('email', '')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        username = validated_data.pop('username', validated_data.get('documento_identidad'))
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        # Crear propietario
        propietario = Propietario.objects.create(user=user, **validated_data)
        return propietario
    
    def update(self, instance, validated_data):
        # Actualizar usuario si se proporcionan datos
        user = instance.user
        if 'email' in validated_data:
            user.email = validated_data.pop('email')
        if 'first_name' in validated_data:
            user.first_name = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user.last_name = validated_data.pop('last_name')
        user.save()
        
        # Actualizar propietario
        return super().update(instance, validated_data)


class UnidadHabitacionalSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(source='propietario.user.get_full_name', read_only=True)
    propietario_documento = serializers.CharField(source='propietario.documento_identidad', read_only=True)
    
    class Meta:
        model = UnidadHabitacional
        fields = ['id', 'propietario', 'propietario_nombre', 'propietario_documento',
                  'numero', 'edificio', 'tipo', 'piso', 'caracteristicas']
    
    def validate_propietario(self, value):
        # Verificar que el propietario no tenga ya una unidad
        if self.instance is None:  # Solo en creación
            if UnidadHabitacional.objects.filter(propietario=value).exists():
                raise serializers.ValidationError("Este propietario ya tiene una unidad asignada.")
        return value


class VehiculoSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(source='propietario.user.get_full_name', read_only=True)
    unidad_numero = serializers.CharField(source='propietario.unidad.numero', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Vehiculo
        fields = ['id', 'propietario', 'propietario_nombre', 'unidad', 'unidad_numero',
                  'placa', 'marca', 'modelo', 'color', 'tipo', 'tipo_display', 'año', 'activo',
                  'foto_vehiculo', 'fecha_registro']
        read_only_fields = ['fecha_registro']


class MascotaSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(source='propietario.user.get_full_name', read_only=True)
    unidad = serializers.CharField(source='propietario.unidad.numero', read_only=True)
    
    class Meta:
        model = Mascota
        fields = ['id', 'propietario', 'propietario_nombre', 'unidad',
                  'nombre', 'tipo', 'raza', 'descripcion']
