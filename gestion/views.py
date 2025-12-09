from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Propietario, UnidadHabitacional, Vehiculo, Mascota
from .serializers import (
    PropietarioSerializer, UnidadHabitacionalSerializer, 
    VehiculoSerializer, MascotaSerializer
)


class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all().select_related('user')
    serializer_class = PropietarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'documento_identidad', 'telefono']
    ordering_fields = ['fecha_registro', 'user__first_name']
    ordering = ['-fecha_registro']


class UnidadHabitacionalViewSet(viewsets.ModelViewSet):
    queryset = UnidadHabitacional.objects.all().select_related('propietario__user')
    serializer_class = UnidadHabitacionalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'edificio']
    search_fields = ['numero', 'edificio', 'propietario__user__first_name', 'propietario__user__last_name']
    ordering_fields = ['numero', 'piso']
    ordering = ['numero']


class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all().select_related('propietario__user', 'propietario__unidad')
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['propietario']
    search_fields = ['placa', 'marca', 'modelo', 'color']
    ordering_fields = ['fecha_registro', 'placa']
    ordering = ['-fecha_registro']

    @action(detail=True, methods=['post'], url_path='generate_qr')
    def generate_qr(self, request, pk=None):
        """Genera un código QR para el vehículo"""
        import qrcode
        from io import BytesIO
        from django.core.files import File
        import os
        
        vehiculo = self.get_object()
        
        # Datos del QR: información del vehículo
        qr_data = f"Vehículo: {vehiculo.placa}\nMarca: {vehiculo.marca}\nModelo: {vehiculo.modelo}\nPropietario: {vehiculo.propietario.user.get_full_name()}"
        
        # Generar QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar en memoria
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Guardar en el modelo (si tienes un campo para QR)
        filename = f'vehiculo_qr_{vehiculo.placa}_{vehiculo.id}.png'
        
        # Crear directorio si no existe
        qr_dir = 'qrcodes_vehiculos'
        os.makedirs(os.path.join('media', qr_dir), exist_ok=True)
        
        # Guardar archivo
        qr_path = os.path.join(qr_dir, filename)
        full_path = os.path.join('media', qr_path)
        
        with open(full_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        # Construir URL completa
        qr_url = request.build_absolute_uri(f'/media/{qr_path}')
        
        return Response({
            'success': True,
            'qr_code_url': qr_url,
            'message': 'QR generado exitosamente'
        })


class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.all().select_related('propietario__user', 'propietario__unidad')
    serializer_class = MascotaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['propietario', 'tipo']
    search_fields = ['nombre', 'raza']
    ordering_fields = ['nombre']
    ordering = ['nombre']


# ENDPOINTS DEL DASHBOARD
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_resumen(request):
    """Resumen general del condominio"""
    from finanzas.models import Expensa
    from mantenimiento.models import Reporte
    from seguridad.models import Visita
    
    total_unidades = UnidadHabitacional.objects.count()
    total_propietarios = Propietario.objects.count()
    total_vehiculos = Vehiculo.objects.count()
    
    # Expensas pendientes
    expensas_pendientes = Expensa.objects.filter(pagada=False).count()
    
    # Reportes pendientes
    reportes_pendientes = Reporte.objects.filter(estado='pendiente').count()
    
    # Visitas hoy
    hoy = timezone.now().date()
    visitas_hoy = Visita.objects.filter(fecha_visita=hoy, estado='programada').count()
    
    return Response({
        'total_unidades': total_unidades,
        'total_propietarios': total_propietarios,
        'total_vehiculos': total_vehiculos,
        'expensas_pendientes': expensas_pendientes,
        'reportes_pendientes': reportes_pendientes,
        'visitas_hoy': visitas_hoy,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_finanzas(request):
    """Datos financieros para el dashboard"""
    from finanzas.models import Expensa, Pago
    
    # Total facturado este mes
    hoy = timezone.now()
    mes_actual = hoy.strftime('%Y-%m')
    
    expensas_mes = Expensa.objects.filter(mes_referencia=mes_actual)
    total_facturado = expensas_mes.aggregate(total=Sum('monto_total'))['total'] or 0
    total_cobrado = expensas_mes.filter(pagada=True).aggregate(total=Sum('monto_total'))['total'] or 0
    pendiente_cobro = total_facturado - total_cobrado
    
    # Tasa de morosidad
    total_expensas = expensas_mes.count()
    expensas_pagas = expensas_mes.filter(pagada=True).count()
    tasa_morosidad = ((total_expensas - expensas_pagas) / total_expensas * 100) if total_expensas > 0 else 0
    
    # Últimos 6 meses
    meses_data = []
    for i in range(5, -1, -1):
        fecha = hoy - timedelta(days=i*30)
        mes = fecha.strftime('%Y-%m')
        total = Expensa.objects.filter(mes_referencia=mes).aggregate(total=Sum('monto_total'))['total'] or 0
        cobrado = Expensa.objects.filter(mes_referencia=mes, pagada=True).aggregate(total=Sum('monto_total'))['total'] or 0
        meses_data.append({
            'mes': mes,
            'facturado': float(total),
            'cobrado': float(cobrado)
        })
    
    return Response({
        'total_facturado': float(total_facturado),
        'total_cobrado': float(total_cobrado),
        'pendiente_cobro': float(pendiente_cobro),
        'tasa_morosidad': round(tasa_morosidad, 2),
        'historico': meses_data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_areas_comunes(request):
    """Estadísticas de áreas comunes"""
    from areas_comunes.models import AreaComun, ReservaAreaComun
    
    total_areas = AreaComun.objects.filter(activa=True).count()
    
    # Reservas este mes
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1)
    reservas_mes = ReservaAreaComun.objects.filter(
        fecha__gte=inicio_mes,
        fecha__lte=hoy
    ).count()
    
    # Áreas más reservadas
    areas_populares = ReservaAreaComun.objects.filter(
        fecha__gte=inicio_mes
    ).values('area__nombre').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    return Response({
        'total_areas': total_areas,
        'reservas_mes': reservas_mes,
        'areas_populares': list(areas_populares)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_riesgos(request):
    """Análisis de riesgos"""
    from finanzas.models import Expensa
    from mantenimiento.models import Reporte
    
    # Propietarios con múltiples expensas pendientes
    propietarios_riesgo = Propietario.objects.annotate(
        expensas_pendientes=Count('expensa', filter=Q(expensa__pagada=False))
    ).filter(expensas_pendientes__gte=2).count()
    
    # Reportes de alta prioridad sin resolver
    reportes_criticos = Reporte.objects.filter(
        prioridad__gte=4,
        estado='pendiente'
    ).count()
    
    return Response({
        'propietarios_en_riesgo': propietarios_riesgo,
        'reportes_criticos': reportes_criticos,
        'nivel_alerta': 'alto' if reportes_criticos > 5 else 'medio' if reportes_criticos > 2 else 'bajo'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_predicciones(request):
    """Predicciones y tendencias"""
    # Datos simulados - aquí se pueden implementar modelos de ML reales
    return Response({
        'tendencia_pagos': 'estable',
        'ocupacion_proyectada': 95.5,
        'ingresos_proyectados': 150000.00,
        'alertas_futuras': []
    })
