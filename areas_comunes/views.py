from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import AreaComun, ReservaAreaComun
from .serializers import AreaComunSerializer, ReservaAreaComunSerializer


class AreaComunViewSet(viewsets.ModelViewSet):
    queryset = AreaComun.objects.all()
    serializer_class = AreaComunSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activa']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'capacidad']
    ordering = ['nombre']


class ReservaAreaComunViewSet(viewsets.ModelViewSet):
    queryset = ReservaAreaComun.objects.all().select_related('propietario__user', 'area', 'propietario__unidad')
    serializer_class = ReservaAreaComunSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['propietario', 'area', 'estado', 'fecha']
    search_fields = ['codigo_reserva', 'propietario__user__first_name', 'area__nombre']
    ordering_fields = ['fecha_reserva', 'fecha']
    ordering = ['-fecha_reserva']
    
    @action(detail=True, methods=['patch'])
    def confirm(self, request, pk=None):
        """Confirmar una reserva pendiente"""
        reserva = self.get_object()
        if reserva.estado != 'pendiente':
            return Response(
                {'detail': 'Solo se pueden confirmar reservas pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reserva.estado = 'confirmada'
        reserva.save()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def cancelar(self, request, pk=None):
        """Cancelar una reserva"""
        reserva = self.get_object()
        if reserva.estado in ['cancelada', 'completada']:
            return Response(
                {'detail': f'No se puede cancelar una reserva {reserva.estado}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reserva.estado = 'cancelada'
        reserva.save()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)
