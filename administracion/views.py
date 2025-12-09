from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from .models import Rol, PerfilUsuario, HistorialAcceso
from .serializers import (
    RolSerializer, PerfilUsuarioSerializer, UserSerializer,
    CrearUsuarioPropietarioSerializer, CrearUsuarioStaffSerializer,
    CambiarPasswordSerializer, HistorialAccesoSerializer
)
from .services import GestorUsuarios
from gestion.models import Propietario


class RolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para Roles.
    """
    queryset = Rol.objects.filter(activo=True)
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios.
    """
    queryset = User.objects.all().select_related('perfil', 'perfil__rol', 'perfil__propietario')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        El endpoint 'me' solo requiere autenticación.
        Los demás endpoints requieren ser admin.
        """
        if self.action == 'me':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Endpoint para obtener información del usuario autenticado.
        GET /api/user/me/
        """
        user = request.user
        try:
            perfil = user.perfil
            rol = perfil.rol.nombre if perfil.rol else 'Sin rol'
            
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'rol': rol,
                'telefono': perfil.telefono,
                'propietario_id': perfil.propietario.id if perfil.propietario else None,
            }, status=status.HTTP_200_OK)
        except PerfilUsuario.DoesNotExist:
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'rol': 'Sin rol',
                'telefono': '',
                'propietario_id': None,
            }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def crear_propietario(self, request):
        """
        Endpoint para crear usuario de propietario manualmente.
        POST /api/administracion/users/crear_propietario/
        Body: {
            "username": "juan",
            "email": "juan@gmail.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "documento_identidad": "8202887",
            "telefono": "78017690"
        }
        """
        serializer = CrearUsuarioPropietarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Obtener el propietario por documento
            propietario = Propietario.objects.get(documento_identidad=serializer.validated_data['documento_identidad'])
            
            # Obtener o crear el rol PROPIETARIO
            from django.contrib.auth.models import Group
            rol_propietario, _ = Rol.objects.get_or_create(
                nombre='PROPIETARIO',
                defaults={
                    'descripcion': 'Propietario de unidad habitacional',
                    'django_group': Group.objects.get_or_create(name='Propietarios')[0]
                }
            )
            
            # Crear el usuario con los datos del formulario
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['documento_identidad'],  # Password = documento
                email=serializer.validated_data['email'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                is_staff=False,
                is_active=True
            )
            
            # Agregar al grupo
            user.groups.add(rol_propietario.django_group)
            
            # Crear o actualizar el perfil
            perfil, _ = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={
                    'rol': rol_propietario,
                    'propietario': propietario,
                    'telefono': serializer.validated_data.get('telefono', ''),
                    'creado_automaticamente': False,
                    'cambio_password_requerido': True,
                    'activo': True
                }
            )
            
            return Response({
                'success': True,
                'message': 'Usuario creado exitosamente',
                'data': {
                    'username': user.username,
                    'password': serializer.validated_data['documento_identidad'],  # Devolver password
                    'email': user.email,
                    'propietario': propietario.nombre
                }
            }, status=status.HTTP_201_CREATED)
        
        except Propietario.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No se encontró un propietario con ese documento de identidad'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def crear_staff(self, request):
        """
        Endpoint para crear usuarios de staff (admin, guardia, conserje, contador).
        POST /api/administracion/users/crear_staff/
        Body: {
            "username": "guardia1",
            "password": "password123",
            "email": "guardia@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "telefono": "12345678",
            "rol": "GUARDIA"
        }
        """
        serializer = CrearUsuarioStaffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = GestorUsuarios.crear_usuario_staff(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
                email=serializer.validated_data['email'],
                rol_nombre=serializer.validated_data['rol'],
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                telefono=serializer.validated_data.get('telefono', '')
            )
            
            return Response({
                'success': True,
                'message': 'Usuario de staff creado exitosamente',
                'data': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        """
        Endpoint para cambiar contraseña.
        POST /api/administracion/users/{id}/cambiar_password/
        Body: {
            "password_actual": "old",  # Opcional para admins
            "password_nueva": "new",
            "password_confirmacion": "new"
        }
        """
        user = self.get_object()
        serializer = CambiarPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Si no es admin, verificar password actual
        if not request.user.is_staff and request.user != user:
            return Response({
                'success': False,
                'error': 'No tienes permisos para cambiar la contraseña de otro usuario'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not request.user.is_staff:
            if not user.check_password(serializer.validated_data.get('password_actual', '')):
                return Response({
                    'success': False,
                    'error': 'Contraseña actual incorrecta'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        GestorUsuarios.cambiar_password(user, serializer.validated_data['password_nueva'])
        
        return Response({
            'success': True,
            'message': 'Contraseña cambiada exitosamente'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def desactivar(self, request, pk=None):
        """
        Desactiva un usuario.
        """
        user = self.get_object()
        GestorUsuarios.desactivar_usuario(user)
        return Response({
            'success': True,
            'message': f'Usuario {user.username} desactivado'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activar(self, request, pk=None):
        """
        Activa un usuario desactivado.
        """
        user = self.get_object()
        GestorUsuarios.activar_usuario(user)
        return Response({
            'success': True,
            'message': f'Usuario {user.username} activado'
        })
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser], url_path='asignar_rol')
    def asignar_rol(self, request, pk=None):
        """
        Asigna o cambia el rol de un usuario.
        PATCH /api/administracion/users/{id}/asignar_rol/
        Body: { "rol": "ADMIN" | "PROPIETARIO" | "GUARDIA" }
        """
        user = self.get_object()
        rol_nombre = request.data.get('rol')
        
        if not rol_nombre:
            return Response({
                'error': 'El campo "rol" es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            rol = Rol.objects.get(nombre=rol_nombre, activo=True)
        except Rol.DoesNotExist:
            return Response({
                'error': f'El rol "{rol_nombre}" no existe o no está activo'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Obtener o crear el perfil del usuario
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
            
            # Asignar el nuevo rol
            perfil.rol = rol
            perfil.save()
            
            # Actualizar los grupos de Django
            user.groups.clear()
            user.groups.add(rol.django_group)
            
            return Response({
                'success': True,
                'message': f'Rol "{rol.get_nombre_display()}" asignado exitosamente',
                'perfil': {
                    'rol': rol.nombre,
                    'rol_display': rol.get_nombre_display(),
                    'telefono': perfil.telefono
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error al asignar rol: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HistorialAccesoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para Historial de Accesos.
    """
    queryset = HistorialAcceso.objects.all().select_related('usuario', 'usuario__perfil')
    serializer_class = HistorialAccesoSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por usuario si se especifica
        usuario_id = self.request.query_params.get('usuario')
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        
        # Filtrar por éxito
        exitoso = self.request.query_params.get('exitoso')
        if exitoso is not None:
            queryset = queryset.filter(exitoso=exitoso.lower() == 'true')
        
        return queryset
