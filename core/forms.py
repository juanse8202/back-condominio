from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Propietario, Guardia

class PropietarioCreationForm(UserCreationForm):
    documento_identidad = forms.CharField(max_length=20)
    telefono = forms.CharField(max_length=15)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Propietario.objects.create(
                user=user,
                documento_identidad=self.cleaned_data['documento_identidad'],
                telefono=self.cleaned_data['telefono']
            )
        return user

class GuardiaCreationForm(UserCreationForm):
    documento_identidad = forms.CharField(max_length=20)
    telefono = forms.CharField(max_length=15)
    turno = forms.CharField(max_length=50)
    fecha_contratacion = forms.DateField()
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Guardia.objects.create(
                user=user,
                documento_identidad=self.cleaned_data['documento_identidad'],
                telefono=self.cleaned_data['telefono'],
                turno=self.cleaned_data['turno'],
                fecha_contratacion=self.cleaned_data['fecha_contratacion']
            )
        return users