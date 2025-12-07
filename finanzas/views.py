from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Expensa, Pago
from .serializers import ExpensaSerializer, PagoSerializer


class ExpensaViewSet(viewsets.ModelViewSet):
    queryset = Expensa.objects.all().select_related('propietario__user', 'propietario__unidad')
    serializer_class = ExpensaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['propietario', 'pagada', 'mes_referencia']
    search_fields = ['mes_referencia', 'propietario__user__first_name', 'propietario__user__last_name']
    ordering_fields = ['fecha_emision', 'fecha_vencimiento', 'monto_total']
    ordering = ['-fecha_emision']


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all().select_related('expensa__propietario__user')
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['verificado', 'metodo_pago', 'expensa__propietario']
    search_fields = ['referencia', 'expensa__propietario__user__first_name']
    ordering_fields = ['fecha_pago', 'monto']
    ordering = ['-fecha_pago']
    
    @action(detail=True, methods=['post'])
    def verificar(self, request, pk=None):
        pago = self.get_object()
        pago.verificado = True
        pago.save()
        
        # Marcar expensa como pagada
        expensa = pago.expensa
        expensa.pagada = True
        from django.utils import timezone
        expensa.fecha_pago = timezone.now()
        expensa.save()
        
        return Response({'status': 'Pago verificado'}, status=status.HTTP_200_OK)
