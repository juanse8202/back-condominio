# serializers.py
from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class UnidadHabitacionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadHabitacional
        fields = '__all__'
        
class PropietarioSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    unidad = UnidadHabitacionalSerializer(read_only=True)  # <--- esto es clave

    class Meta:
        model = Propietario
        fields = '__all__'

class ExpensaSerializer(serializers.ModelSerializer):
    propietario = PropietarioSerializer(read_only=True)  # <--- esto es clave

    class Meta:
        model = Expensa
        fields = '__all__'

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaAreaComun
        fields = '__all__'

class VisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visita
        fields = '__all__'

class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = '__all__'

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Agrega los datos del usuario
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'is_staff': self.user.is_staff,
        }
        return data