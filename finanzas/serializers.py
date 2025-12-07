from rest_framework import serializers
from .models import Expensa, Pago


class ExpensaSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(source='propietario.user.get_full_name', read_only=True)
    unidad = serializers.CharField(source='propietario.unidad.numero', read_only=True)
    estado = serializers.SerializerMethodField()
    
    class Meta:
        model = Expensa
        fields = ['id', 'propietario', 'propietario_nombre', 'unidad', 'mes_referencia',
                  'monto_total', 'cuota_basica', 'multas', 'reservas', 'otros',
                  'fecha_emision', 'fecha_vencimiento', 'pagada', 'fecha_pago', 'estado']
        read_only_fields = ['fecha_emision', 'fecha_pago']
    
    def get_estado(self, obj):
        if obj.pagada:
            return 'Pagada'
        from django.utils import timezone
        if obj.fecha_vencimiento < timezone.now().date():
            return 'Vencida'
        return 'Pendiente'


class PagoSerializer(serializers.ModelSerializer):
    expensa_detalle = serializers.SerializerMethodField()
    propietario_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Pago
        fields = ['id', 'expensa', 'expensa_detalle', 'propietario_nombre', 'monto', 
                  'metodo_pago', 'referencia', 'fecha_pago', 'comprobante', 'verificado']
        read_only_fields = ['fecha_pago']
    
    def get_expensa_detalle(self, obj):
        return f"{obj.expensa.mes_referencia} - {obj.expensa.monto_total}"
    
    def get_propietario_nombre(self, obj):
        return obj.expensa.propietario.user.get_full_name()
    
    def create(self, validated_data):
        pago = super().create(validated_data)
        # Si el pago es verificado, marcar la expensa como pagada
        if pago.verificado:
            expensa = pago.expensa
            expensa.pagada = True
            from django.utils import timezone
            expensa.fecha_pago = timezone.now()
            expensa.save()
        return pago
