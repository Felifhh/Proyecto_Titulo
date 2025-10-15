from django import forms
from datetime import date
from django.core.exceptions import ValidationError
from .models import Actividad
from Reserva.models import Reserva

class ActividadForm(forms.ModelForm):
    vincular_reserva = forms.ModelChoiceField(
        queryset=Reserva.objects.none(),
        required=False,
        label="Vincular a mi reserva",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # Horas disponibles: de 08:00 a 22:00
    HORA_CHOICES = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(8, 23)]

    hora_inicio = forms.ChoiceField(
        choices=HORA_CHOICES,
        required=False,
        label="Hora de inicio",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    hora_fin = forms.ChoiceField(
        choices=HORA_CHOICES,
        required=False,
        label="Hora de fin",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Actividad
        fields = ["titulo", "ubicacion", "descripcion", "fecha", "hora_inicio", "hora_fin", "cupos", "vincular_reserva"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "ubicacion": forms.TextInput(attrs={"class": "form-control", "readonly": False}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "cupos": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

    def __init__(self, *args, **kwargs):
        vecino = kwargs.pop("vecino", None)
        super().__init__(*args, **kwargs)

        if vecino is not None:
            # Mostrar solo reservas activas y futuras del vecino
            self.fields["vincular_reserva"].queryset = (
                Reserva.objects
                .filter(id_vecino=vecino, estado='Activa', fecha__gte=date.today())
                .order_by("fecha", "hora_inicio")
            )

        self.fields["vincular_reserva"].empty_label = "— Sin vincular —"

    def clean(self):
        cd = super().clean()
        reserva = cd.get("vincular_reserva")

        # Si se vincula una reserva → rellenar datos automáticamente
        if reserva:
            cd["fecha"] = reserva.fecha
            cd["hora_inicio"] = reserva.hora_inicio.strftime("%H:%M")
            cd["hora_fin"] = reserva.hora_fin.strftime("%H:%M")
            cd["ubicacion"] = reserva.id_espacio.nombre  # <-- ubicación del espacio comunal

            if cd["hora_fin"] <= cd["hora_inicio"]:
                raise ValidationError("La hora de fin de la reserva debe ser mayor que la de inicio.")
            return cd

        # Si no hay reserva → validar manualmente
        fecha = cd.get("fecha")
        hi = cd.get("hora_inicio")
        hf = cd.get("hora_fin")

        if not fecha:
            self.add_error("fecha", "Debes ingresar la fecha.")
        if not hi:
            self.add_error("hora_inicio", "Debes elegir la hora de inicio.")
        if not hf:
            self.add_error("hora_fin", "Debes elegir la hora de fin.")

        if self.errors:
            return cd

        if hf <= hi:
            self.add_error("hora_fin", "La hora de fin debe ser mayor que la hora de inicio.")
        return cd
