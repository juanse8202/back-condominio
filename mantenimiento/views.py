from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Reporte
from .serializers import ReporteSerializer


class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.all().select_related('propietario__user', 'propietario__unidad')
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'estado', 'prioridad', 'propietario']
    search_fields = ['titulo', 'descripcion', 'ubicacion']
    ordering_fields = ['fecha_reporte', 'prioridad']
    ordering = ['-fecha_reporte']
