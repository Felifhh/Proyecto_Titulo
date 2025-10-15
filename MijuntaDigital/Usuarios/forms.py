from django import forms
from django.contrib.auth.hashers import make_password
from .models import Vecino, Rol
from .validators import validar_dv, formatear_run, validar_contrasena  # Ajusta si tus validadores están en otro módulo

class RegistroVecinoForm(forms.ModelForm):
    run = forms.CharField(label="RUN", max_length=15)
    nombre = forms.CharField(label="Nombre completo", max_length=100)
    direccion = forms.CharField(label="Dirección", max_length=200, required=False)
    correo = forms.EmailField(label="Correo electrónico", required=False)
    telefono = forms.CharField(label="Teléfono", max_length=20, required=False)

    # Campos de contraseña
    contrasena = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Debe tener al menos 7 caracteres, una mayúscula y un número."
    )
    repetir_contrasena = forms.CharField(
        label="Repetir contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # Evidencia de residencia
    evidencia = forms.FileField(
        label="Evidencia de residencia (boleta, certificado, etc.)",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Vecino
        fields = [
            'run', 'nombre', 'direccion', 'correo', 'telefono',
            'contrasena', 'repetir_contrasena', 'evidencia'
        ]

    # --- Validaciones personalizadas ---
    def clean_run(self):
        run = self.cleaned_data['run']
        if not validar_dv(run):
            raise forms.ValidationError("RUN inválido (verifica dígito verificador).")
        return formatear_run(run)

    def clean_contrasena(self):
        contrasena = self.cleaned_data['contrasena']
        if not validar_contrasena(contrasena):
            raise forms.ValidationError(
                "La contraseña debe tener al menos 7 caracteres, incluir 1 mayúscula y 1 número."
            )
        return contrasena

    def clean(self):
        cleaned_data = super().clean()
        c1 = cleaned_data.get("contrasena")
        c2 = cleaned_data.get("repetir_contrasena")
        if c1 and c2 and c1 != c2:
            self.add_error("repetir_contrasena", "Las contraseñas no coinciden.")
        return cleaned_data

    # --- Guardado ---
    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.estado = 'Pendiente'

        # Asignar rol "Vecino"
        try:
            rol_vecino = Rol.objects.get(nombre='Vecino')
        except Rol.DoesNotExist:
            rol_vecino = Rol.objects.create(nombre='Vecino')
        obj.id_rol = rol_vecino

        # Hashear contraseña
        obj.contrasena = make_password(self.cleaned_data['contrasena'])

        #  Asignar imagen por defecto si no hay foto
        if not obj.foto:
            obj.foto = 'perfiles/default.png'

        if commit:
            obj.save()
        return obj



class FotoPerfilForm(forms.ModelForm):
    class Meta:
        model = Vecino
        fields = ['foto']


class LoginForm(forms.Form):
    run = forms.CharField(label="RUN", max_length=15)
    contrasena = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
