from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Visita, RegistroVisita, Guardia, ComunicacionGuardia
from .serializers import (
    VisitaSerializer, RegistroVisitaSerializer, 
    GuardiaSerializer, ComunicacionGuardiaSerializer
)


class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all().select_related('propietario__user', 'propietario__unidad')
    serializer_class = VisitaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['propietario', 'estado', 'fecha_visita']
    search_fields = ['nombre_visitante', 'documento_identidad', 'codigo_acceso']
    ordering_fields = ['fecha_visita', 'fecha_creacion']
    ordering = ['-fecha_creacion']


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
