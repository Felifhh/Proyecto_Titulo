from django import forms
from .models import Documento


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'tipo', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo':  forms.TextInput(attrs={'class': 'form-control'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
