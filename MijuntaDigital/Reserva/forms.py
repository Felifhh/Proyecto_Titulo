from django import forms
from .models import EspacioComunal


class EspacioForm(forms.ModelForm):
    """Formulario para crear o editar un espacio comunal."""
    class Meta:
        model = EspacioComunal
        fields = ['nombre', 'descripcion', 'monto_hora', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del espacio'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'monto_hora': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
