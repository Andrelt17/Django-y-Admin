from django import forms
from clientes.models import Cliente
from rutas.models import Ruta
from .models import Encomienda
from config.choices import EstadoGeneral


class EncomiendaForm(forms.ModelForm):
    class Meta:
        model = Encomienda
        fields = [
            'descripcion',
            'peso',
            'remitente',
            'destinatario',
            'ruta',
            'empleado',
            'estado',
            'fecha_entrega_est',
            'fecha_entrega_real',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la encomienda',
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
            }),
            'remitente': forms.Select(attrs={'class': 'form-select'}),
            'destinatario': forms.Select(attrs={'class': 'form-select'}),
            'ruta': forms.Select(attrs={'class': 'form-select'}),
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_entrega_est': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'fecha_entrega_real': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['remitente'].queryset = Cliente.objects.activos()
        self.fields['destinatario'].queryset = Cliente.objects.activos()
        self.fields['ruta'].queryset = Ruta.objects.filter(estado=EstadoGeneral.ACTIVO)
        self.fields['remitente'].label = 'Remitente'
        self.fields['destinatario'].label = 'Destinatario'
        self.fields['ruta'].label = 'Ruta'
        self.fields['empleado'].label = 'Empleado'
        self.fields['estado'].label = 'Estado'
        self.fields['fecha_entrega_est'].label = 'Fecha entrega estimada'
        self.fields['fecha_entrega_real'].label = 'Fecha entrega real'


class EstadoCambioForm(forms.ModelForm):
    class Meta:
        model = Encomienda
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'estado': 'Cambiar estado',
        }
