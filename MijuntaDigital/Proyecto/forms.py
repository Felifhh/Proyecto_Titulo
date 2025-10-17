from django import forms
from .models import Proyecto
import os

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'presupuesto', 'documento_adj']
        labels = {
            'titulo': 'Título del proyecto',
            'descripcion': 'Descripción',
            'presupuesto': 'Presupuesto estimado',
            'documento_adj': 'Imagen de referencia',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Mejoramiento de área verde'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe el objetivo y beneficios del proyecto'}),
            'presupuesto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monto estimado en pesos'}),
            'documento_adj': forms.ClearableFileInput(attrs={
                'class': 'form-control',   # ✅ visible y compatible con Bootstrap
                'accept': 'image/*'
            }),
        }

    def clean_documento_adj(self):
        imagen = self.cleaned_data.get('documento_adj')

        # ⚠️ Verifica que se haya subido algo
        if not imagen:
            raise forms.ValidationError("Debe subir una imagen de referencia obligatoriamente.")

        # ⚙️ Si es un string (ruta ya guardada), omitir validación
        if isinstance(imagen, str):
            return imagen

        # 🧩 Validar extensión si es un archivo nuevo
        nombre = getattr(imagen, 'name', '')
        ext = os.path.splitext(nombre)[1].lower()

        if ext not in ['.jpg', '.jpeg', '.png']:
            raise forms.ValidationError("Solo se permiten imágenes en formato JPG o PNG.")

        return imagen

