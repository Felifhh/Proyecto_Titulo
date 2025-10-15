from django import forms
from .models import Certificado

class SolicitudCertificadoForm(forms.ModelForm):
    motivo = forms.CharField(
        label="Motivo de la solicitud",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    class Meta:
        model = Certificado
        fields = ['motivo']