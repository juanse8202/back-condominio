# views.py para móvil
from rest_framework import viewsets, permissions
from .models import *
from .serializers import *
from datetime import date

class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all()
    serializer_class = PropietarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Propietario.objects.filter(user=self.request.user)

class ExpensaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExpensaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        propietario = Propietario.objects.get(user=self.request.user)
        return Expensa.objects.filter(propietario=propietario)

class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        propietario = Propietario.objects.get(user=self.request.user)
        return ReservaAreaComun.objects.filter(propietario=propietario)

class VisitaViewSet(viewsets.ModelViewSet):
    serializer_class = VisitaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        propietario = Propietario.objects.get(user=self.request.user)
        return Visita.objects.filter(propietario=propietario)

class ReporteViewSet(viewsets.ModelViewSet):
    serializer_class = ReporteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        propietario = Propietario.objects.get(user=self.request.user)
        return Reporte.objects.filter(propietario=propietario)
    


    # views.py para web admin
from rest_framework import viewsets, permissions
from .models import *

class AdminPropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all()
    serializer_class = PropietarioSerializer
    permission_classes = [permissions.IsAdminUser]
    
class AdminExpensaViewSet(viewsets.ModelViewSet):
    queryset = Expensa.objects.all()
    serializer_class = ExpensaSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminVisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all()
    serializer_class = VisitaSerializer
    permission_classes = [permissions.IsAdminUser]

class GuardiaVisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all()
    serializer_class = VisitaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Lógica para que guardias solo vean visitas del día
        return Visita.objects.filter(fecha_visita=date.today())
    
from rest_framework_simplejwt.views import TokenObtainPairView
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer