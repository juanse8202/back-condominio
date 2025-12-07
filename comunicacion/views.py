from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Comunicado
from .serializers import ComunicadoSerializer


class ComunicadoViewSet(viewsets.ModelViewSet):
    queryset = Comunicado.objects.all().select_related('autor')
    serializer_class = ComunicadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'prioridad', 'activo']
    search_fields = ['titulo', 'contenido']
    ordering_fields = ['fecha_publicacion', 'prioridad']
    ordering = ['-fecha_publicacion']
    
    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)
