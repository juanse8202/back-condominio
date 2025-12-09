from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Rol, PerfilUsuario, HistorialAcceso


class RolSerializer(serializers.ModelSerializer):
    nombre_display = serializers.CharField(source='get_nombre_display', read_only=True)
    
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'nombre_display', 'descripcion', 'activo', 'fecha_creacion']
        read_only_fields = ['fecha_creacion']


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    rol_display = serializers.CharField(source='rol.get_nombre_display', read_only=True)
    propietario_nombre = serializers.CharField(source='propietario.nombre', read_only=True)
    
    class Meta:
        model = PerfilUsuario
        fields = [
            'id', 'rol', 'rol_display', 'propietario', 'propietario_nombre',
            'telefono', 'foto', 'activo', 'creado_automaticamente',
            'cambio_password_requerido', 'fecha_creacion', 'ultima_actualizacion'
        ]
        read_only_fields = ['creado_automaticamente', 'fecha_creacion', 'ultima_actualizacion']


class UserSerializer(serializers.ModelSerializer):
    perfil = serializers.SerializerMethodField()
    rol = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'date_joined', 'last_login',
            'perfil', 'rol'
        ]
        read_only_fields = ['date_joined', 'last_login']
    
    def get_perfil(self, obj):
        if hasattr(obj, 'perfil'):
            # Obtener teléfono del perfil o del propietario vinculado
            telefono = obj.perfil.telefono
            if not telefono and obj.perfil.propietario:
                telefono = obj.perfil.propietario.telefono
            
            return {
                'id': obj.perfil.id,
                'rol': obj.perfil.rol.nombre if obj.perfil.rol else None,
                'rol_display': obj.perfil.rol.get_nombre_display() if obj.perfil.rol else 'Sin rol',
                'telefono': telefono,
                'activo': obj.perfil.activo,
            }
        return None
    
    def get_rol(self, obj):
        if hasattr(obj, 'perfil') and obj.perfil.rol:
            return obj.perfil.rol.get_nombre_display()
        return 'Sin rol'


class CrearUsuarioPropietarioSerializer(serializers.Serializer):
    """
    Serializer para crear usuario de propietario manualmente.
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    documento_identidad = serializers.CharField(max_length=50)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya existe")
        return value
    
    def validate_documento_identidad(self, value):
        from gestion.models import Propietario
        # Verificar que exista un propietario con ese documento
        try:
            propietario = Propietario.objects.get(documento_identidad=value)
        except Propietario.DoesNotExist:
            raise serializers.ValidationError("No existe un propietario con este documento de identidad")
        
        # Verificar que no tenga usuario ya asignado en PerfilUsuario
        if PerfilUsuario.objects.filter(propietario=propietario).exists():
            raise serializers.ValidationError("Este propietario ya tiene un usuario asignado")
        
        return value


class CrearUsuarioStaffSerializer(serializers.Serializer):
    """
    Serializer para crear usuarios de staff (admin, guardia, etc).
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=4)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    rol = serializers.ChoiceField(choices=[
        ('ADMIN', 'Administrador'),
        ('GUARDIA', 'Guardia de Seguridad'),
    ])
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya existe")
        return value


class CambiarPasswordSerializer(serializers.Serializer):
    """
    Serializer para cambiar contraseña.
    """
    password_actual = serializers.CharField(write_only=True, required=False)
    password_nueva = serializers.CharField(write_only=True, min_length=4)
    password_confirmacion = serializers.CharField(write_only=True, min_length=4)
    
    def validate(self, data):
        if data['password_nueva'] != data['password_confirmacion']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data


class HistorialAccesoSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = HistorialAcceso
        fields = [
            'id', 'usuario', 'usuario_username', 'usuario_nombre',
            'fecha_hora', 'ip_address', 'user_agent', 'exitoso'
        ]
        read_only_fields = fields
