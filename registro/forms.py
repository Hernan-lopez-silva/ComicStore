from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente, Pais, Region, Comuna
from django.db import transaction
import re
from django.core.exceptions import ValidationError

class FormCliente(UserCreationForm):
    nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-3'}), label="Nombre:", error_messages={'required': 'El nombre es obligatorio.'})
    apellido = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-3'}), label="Apellido:", error_messages={'required': 'El apellido es obligatorio.'})
    rut = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-3'}), label="RUT:", error_messages={'required': 'El RUT es obligatorio.'})
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control mb-3'}), label="Correo electrónico:", error_messages={'required': 'El correo es obligatorio.'})
    telefono = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-3'}), label="Teléfono:", error_messages={'required': 'El teléfono es obligatorio.'})
    direccion = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-3'}), label="Dirección:", error_messages={'required': 'La dirección es obligatoria.'})
    pais = forms.CharField(widget=forms.Select(attrs={'class': 'form-control mb-3', 'id':'pais'}), label="País:")
    region = forms.CharField(widget=forms.Select(attrs={'class': 'form-control mb-3', 'id':'region'}), label="Región:")
    comuna = forms.CharField(widget=forms.Select(attrs={'class': 'form-control mb-3', 'id':'comuna'}), label="Comuna:")
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'}), label="Contraseña:", error_messages={'required': 'La contraseña es obligatoria.'})
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'}), label="Confirmar contraseña:", error_messages={'required': 'La confirmación de la contraseña es obligatoria.'})
    
    class Meta:
        model = User
        fields = [
            'username',
            'nombre',
            'apellido',
            'rut',
            'email',
            'telefono',
            'direccion',
            'pais',
            'region',
            'comuna',
            'password1',
            'password2',
        ]
        labels = {
            'username': 'Nombre de usuario:',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            cliente = Cliente(user=user, nombre=self.cleaned_data['nombre'], apellido=self.cleaned_data['apellido'], rut=self.cleaned_data['rut'], telefono=self.cleaned_data['telefono'], direccion=self.cleaned_data['direccion'], pais=self.cleaned_data.get('pais'), region=self.cleaned_data.get('region'), comuna=self.cleaned_data.get('comuna'))
            cliente.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super(FormCliente, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['username'].error_messages = {'required': 'El nombre de usuario es obligatorio.'}
        self.fields['pais'].required = True
        self.fields['pais'].error_messages = {'required': 'El país es obligatorio.'}
        self.fields['region'].required = True
        self.fields['region'].error_messages = {'required': 'La región es obligatoria.'}
        self.fields['comuna'].required = True
        self.fields['comuna'].error_messages = {'required': 'La comuna es obligatoria.'}

    def clean_rut(self):
        rut = self.cleaned_data['rut']
        pattern = r'^\d{6,8}-[\dKk]$'
        if not re.match(pattern, rut):
            raise ValidationError("Ingrese rut sin puntos y con guión")
        elif Cliente.objects.filter(rut=rut).exists():
            raise ValidationError("El rut ya está registrado.")
        return rut    

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("El correo ya está registrado.")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        pattern = r'^\+569\d{8}$'
        if not re.match(pattern, telefono):
            raise ValidationError("Ingrese un número con formato +56912345678")
        return telefono 

    def clean(self):
        super(FormCliente, self).clean()  # No olvides llamar al método clean de la superclase
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')

        # Asegúrate de devolver los datos limpios
        return self.cleaned_data