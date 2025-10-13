from django import forms
from .models import EspacioComunal
from .models import Reserva
from django.utils.timezone import now
from datetime import datetime


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


class ReservaForm(forms.ModelForm):
    # Generamos las horas completas de 08:00 a 20:00
    OPCIONES_HORAS = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(8, 21)]

    hora_inicio = forms.ChoiceField(
        choices=OPCIONES_HORAS,
        label="Hora de inicio",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    hora_fin = forms.ChoiceField(
        choices=OPCIONES_HORAS,
        label="Hora de término",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Reserva
        fields = ['fecha', 'hora_inicio', 'hora_fin', 'observacion']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        if hora_inicio and hora_fin:
            hora_inicio_dt = datetime.strptime(hora_inicio, "%H:%M").time()
            hora_fin_dt = datetime.strptime(hora_fin, "%H:%M").time()

            if hora_inicio_dt >= hora_fin_dt:
                raise forms.ValidationError("La hora de inicio debe ser menor que la hora de término.")
        return cleaned_data
