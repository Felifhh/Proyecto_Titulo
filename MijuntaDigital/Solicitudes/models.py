from django.db import models
from Usuarios.models import Vecino


class Solicitud(models.Model):
    TIPOS = [
        ('Mantención', 'Mantención'),
        ('Luminarias', 'Luminarias'),
        ('Aseo', 'Aseo'),
        ('Otro', 'Otro'),
    ]

    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Resuelta', 'Resuelta'),
        ('Rechazada', 'Rechazada'),
    ]

    id_solicitud = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey(Vecino, on_delete=models.CASCADE, db_column='id_vecino')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='Otro')
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'solicitud'
        verbose_name = 'Solicitud Ciudadana'
        verbose_name_plural = 'Solicitudes Ciudadanas'

    def __str__(self):
        return f"{self.tipo} - {self.estado} ({self.id_vecino.nombre})"
