from django.db import models
from Usuarios.models import Vecino


class Documento(models.Model):
    TIPOS = [
        ('Acta', 'Acta'),
        ('Estatuto', 'Estatuto'),
        ('Reglamento', 'Reglamento'),
        ('Oficio', 'Oficio'),
    ]

    id_documento = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='documentos/')
    texto_extraido = models.TextField(blank=True, null=True)
    version = models.IntegerField(default=1)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    id_vecino = models.ForeignKey(Vecino, on_delete=models.CASCADE, db_column='id_vecino', null=True, blank=True)

    class Meta:
        db_table = 'documento'

    def __str__(self):
        return f"{self.titulo} (v{self.version})"


