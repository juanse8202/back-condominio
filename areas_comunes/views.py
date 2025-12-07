from rest_framework import viewsets, filters
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
