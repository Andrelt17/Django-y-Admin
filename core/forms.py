from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label='Nombre', max_length=120, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Tu nombre',
    }))
    email = forms.EmailField(label='Correo electrónico', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Tu correo',
    }))
    message = forms.CharField(label='Mensaje', widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Escribe tu mensaje',
        'rows': 4,
    }))
