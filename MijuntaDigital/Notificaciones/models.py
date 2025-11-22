# Notificaciones/models.py
from django.db import models

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('global', 'Global (todos)'),
        ('directorio', 'Solo Directorio'),
    ]
    id_notificacion = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='global')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.tipo}] {self.titulo}"


class NotificacionUsuario(models.Model):
    """
    Estado por usuario (leída/no leída). Usa el id del vecino que ya manejas en sesión.
    """
    id = models.AutoField(primary_key=True)
    notificacion = models.ForeignKey(Notificacion, on_delete=models.CASCADE, related_name='destinatarios')
    id_vecino = models.IntegerField()  # o ForeignKey a Usuarios.Vecino si te conviene
    leida = models.BooleanField(default=False)
    fecha_estado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('notificacion', 'id_vecino')
