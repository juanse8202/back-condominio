from rest_framework import serializers
from .models import Pago


class PagoSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(
        source='propietario.user.get_full_name',
        read_only=True
    )
    reserva_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Pago
        fields = [
            'id',
            'propietario',
            'propietario_nombre',
            'reserva',
            'reserva_info',
            'tipo_pago',
            'monto',
            'moneda',
            'payment_intent_id',
            'payment_method_id',
            'charge_id',
            'estado',
            'descripcion',
            'metadata',
            'fecha_creacion',
            'fecha_actualizacion',
            'fecha_completado',
        ]
        read_only_fields = [
            'id',
            'propietario_nombre',
            'reserva_info',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
    
    def get_reserva_info(self, obj):
        if obj.reserva:
            return {
                'id': obj.reserva.id,
                'area': obj.reserva.area_comun.nombre,
                'fecha': obj.reserva.fecha.isoformat(),
                'hora_inicio': str(obj.reserva.hora_inicio),
                'hora_fin': str(obj.reserva.hora_fin),
            }
        return None


class CreatePaymentIntentSerializer(serializers.Serializer):
    """Serializer para crear un Payment Intent"""
    reserva_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value


class ConfirmPaymentSerializer(serializers.Serializer):
    """Serializer para confirmar un pago"""
    payment_intent_id = serializers.CharField(max_length=255)
    card_number = serializers.CharField(max_length=16)
    exp_month = serializers.CharField(max_length=2)
    exp_year = serializers.CharField(max_length=2)
    cvc = serializers.CharField(max_length=4)
    
    def validate_card_number(self, value):
        # Remover espacios
        value = value.replace(' ', '')
        if not value.isdigit() or len(value) != 16:
            raise serializers.ValidationError("Número de tarjeta inválido")
        return value
    
    def validate_exp_month(self, value):
        if not value.isdigit() or not (1 <= int(value) <= 12):
            raise serializers.ValidationError("Mes de expiración inválido")
        return value
    
    def validate_exp_year(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Año de expiración inválido")
        return value
    
    def validate_cvc(self, value):
        if not value.isdigit() or len(value) not in [3, 4]:
            raise serializers.ValidationError("CVC inválido")
        return value
