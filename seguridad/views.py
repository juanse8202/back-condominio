from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Visita, RegistroVisita, Guardia, ComunicacionGuardia, PlateRecognitionLog
from .serializers import (
    VisitaSerializer, RegistroVisitaSerializer, 
    GuardiaSerializer, ComunicacionGuardiaSerializer,
    PlateRecognitionLogSerializer
)
from .plate_recognizer import PlateRecognizerService
from gestion.models import Vehiculo


class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all().select_related('propietario__user', 'propietario__unidad')
    serializer_class = VisitaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['propietario', 'estado', 'fecha_visita']
    search_fields = ['nombre_visitante', 'documento_identidad', 'codigo_acceso']
    ordering_fields = ['fecha_visita', 'fecha_creacion']
    ordering = ['-fecha_creacion']
    
    @action(detail=False, methods=['post'])
    def recognize_plate(self, request):
        """
        Endpoint para reconocer placa vehicular usando Plate Recognizer
        POST /api/seguridad/visitas/recognize_plate/
        Body: multipart/form-data con 'image' file
        """
        print(f"[PLATE RECOGNIZER] Request FILES: {request.FILES.keys()}")
        print(f"[PLATE RECOGNIZER] Request DATA: {request.data.keys()}")
        
        if 'image' not in request.FILES:
            error_msg = 'No se proporcionó ninguna imagen'
            print(f"[PLATE RECOGNIZER ERROR] {error_msg}")
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        print(f"[PLATE RECOGNIZER] Imagen recibida: {image_file.name}, tipo: {image_file.content_type}, tamaño: {image_file.size}")
        
        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if image_file.content_type not in allowed_types:
            error_msg = f'Tipo de archivo no permitido: {image_file.content_type}. Use JPG o PNG'
            print(f"[PLATE RECOGNIZER ERROR] {error_msg}")
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar tamaño (máximo 5MB)
        if image_file.size > 5 * 1024 * 1024:
            error_msg = f'La imagen es demasiado grande: {image_file.size} bytes. Máximo 5MB'
            print(f"[PLATE RECOGNIZER ERROR] {error_msg}")
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Procesar imagen con Plate Recognizer
        print(f"[PLATE RECOGNIZER] Llamando al servicio de reconocimiento...")
        service = PlateRecognizerService()
        result = service.recognize_plate(image_file)
        
        print(f"[PLATE RECOGNIZER] Resultado del servicio: {result}")
        
        if not result['success']:
            print(f"[PLATE RECOGNIZER ERROR] {result.get('error', 'Error desconocido')}")
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar si el vehículo está registrado
        vehiculo = None
        unidad = None
        vehicle_registered = False
        tipo_acceso = 'desconocido'
        
        try:
            vehiculo = Vehiculo.objects.select_related(
                'propietario__user', 
                'propietario__unidad',
                'unidad'
            ).get(placa=result['plate_number'])
            
            vehicle_registered = True
            tipo_acceso = 'residente'
            unidad = vehiculo.unidad or vehiculo.propietario.unidad
            
        except Vehiculo.DoesNotExist:
            # Verificar si es una visita programada
            try:
                visita = Visita.objects.select_related('propietario__unidad').filter(
                    placa_vehiculo=result['plate_number'],
                    estado='programada'
                ).first()
                
                if visita:
                    tipo_acceso = 'visita'
                    unidad = visita.propietario.unidad
                    
            except Exception:
                pass
        
        # Guardar log de reconocimiento
        log = PlateRecognitionLog.objects.create(
            plate_number=result['plate_number'],
            plate_region=result.get('region', ''),
            vehicle_type=result.get('vehicle_type', ''),
            vehicle_make=result.get('vehicle_make', ''),
            vehicle_model=result.get('vehicle_model', ''),
            vehicle_color=result.get('vehicle_color', ''),
            image=image_file,
            confidence=result['confidence'],
            confidence_score=result.get('confidence_score'),
            raw_response=result.get('raw_response'),
            vehiculo=vehiculo,
            unidad=unidad,
            is_registered=vehicle_registered,
            tipo_acceso=tipo_acceso,
            acceso_permitido=vehicle_registered,  # Auto-aprobar si está registrado
            acceso_automatico=vehicle_registered,
            guardia=request.user.guardia if hasattr(request.user, 'guardia') else None
        )
        
        # Preparar respuesta
        response_data = {
            'success': True,
            'log_id': log.id,
            'plate_number': result['plate_number'],
            'confidence': result['confidence'],
            'confidence_score': result.get('confidence_score'),
            'vehicle_registered': vehicle_registered,
            'tipo_acceso': tipo_acceso,
            'acceso_permitido': log.acceso_permitido,
            'processing_time': result.get('processing_time')
        }
        
        # Agregar información detectada por Plate Recognizer
        if result.get('vehicle_type'):
            response_data['detected_info'] = {
                'type': result.get('vehicle_type'),
                'make': result.get('vehicle_make'),
                'model': result.get('vehicle_model'),
                'color': result.get('vehicle_color'),
                'region': result.get('region')
            }
        
        # Agregar información del vehículo registrado
        if vehiculo:
            response_data['vehicle_info'] = {
                'id': vehiculo.id,
                'placa': vehiculo.placa,
                'marca': vehiculo.marca,
                'modelo': vehiculo.modelo,
                'color': vehiculo.color,
                'año': vehiculo.año,
                'propietario': vehiculo.propietario.user.get_full_name(),
                'unidad': str(unidad) if unidad else None
            }
        else:
            response_data['message'] = 'Vehículo no registrado en el sistema'
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class RegistroVisitaViewSet(viewsets.ModelViewSet):
    queryset = RegistroVisita.objects.all().select_related('visita__propietario', 'guardia')
    serializer_class = RegistroVisitaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['visita', 'guardia']
    search_fields = ['visita__nombre_visitante', 'observaciones']
    ordering_fields = ['hora_entrada', 'hora_salida']
    ordering = ['-hora_entrada']


class GuardiaViewSet(viewsets.ModelViewSet):
    queryset = Guardia.objects.all().select_related('user')
    serializer_class = GuardiaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['turno', 'activo']
    search_fields = ['nombre', 'telefono']
    ordering = ['nombre']


class ComunicacionGuardiaViewSet(viewsets.ModelViewSet):
    queryset = ComunicacionGuardia.objects.all().select_related('guardia', 'propietario__user')
    serializer_class = ComunicacionGuardiaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['guardia', 'propietario', 'tipo', 'leido']
    search_fields = ['mensaje']
    ordering_fields = ['fecha_comunicacion']
    ordering = ['-fecha_comunicacion']


class PlateRecognitionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar historial de reconocimientos de placas
    GET /api/seguridad/plate-recognition-logs/
    """
    queryset = PlateRecognitionLog.objects.all().select_related(
        'vehiculo__propietario__user',
        'unidad__propietario__user',
        'guardia__user'
    )
    serializer_class = PlateRecognitionLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'plate_number', 
        'is_registered', 
        'tipo_acceso',
        'acceso_permitido', 
        'confidence',
        'vehiculo',
        'unidad'
    ]
    search_fields = ['plate_number', 'observaciones']
    ordering_fields = ['fecha_reconocimiento', 'confidence_score']
    ordering = ['-fecha_reconocimiento']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Estadísticas de reconocimientos de placas
        GET /api/seguridad/plate-recognition-logs/stats/
        """
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        # Últimos 30 días
        fecha_inicio = datetime.now() - timedelta(days=30)
        
        logs = PlateRecognitionLog.objects.filter(
            fecha_reconocimiento__gte=fecha_inicio
        )
        
        stats = {
            'total_reconocimientos': logs.count(),
            'vehiculos_registrados': logs.filter(is_registered=True).count(),
            'vehiculos_no_registrados': logs.filter(is_registered=False).count(),
            'accesos_permitidos': logs.filter(acceso_permitido=True).count(),
            'accesos_denegados': logs.filter(acceso_permitido=False).count(),
            'por_tipo_acceso': dict(
                logs.values('tipo_acceso').annotate(count=Count('id')).values_list('tipo_acceso', 'count')
            ),
            'por_confianza': dict(
                logs.values('confidence').annotate(count=Count('id')).values_list('confidence', 'count')
            ),
            'ultimos_reconocimientos': PlateRecognitionLogSerializer(
                logs.order_by('-fecha_reconocimiento')[:10],
                many=True,
                context={'request': request}
            ).data
        }
        
        return Response(stats)
