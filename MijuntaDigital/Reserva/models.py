from django.db import models
from Usuarios.models import Vecino

class EspacioComunal(models.Model):
    ESTADOS = [
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ]
    id_espacio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    monto_hora = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='espacios/', null=False, blank=False)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'espacio_comunal'

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
        ('Cancelada', 'Cancelada'),
    ]
    id_reserva = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey(Vecino, on_delete=models.CASCADE, db_column='id_vecino')
    id_espacio = models.ForeignKey(EspacioComunal, on_delete=models.CASCADE, db_column='id_espacio')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Activa')
    observacion = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField()

    class Meta:
        db_table = 'reserva'

    def __str__(self):
        return f"{self.id_espacio.nombre} ({self.fecha})"
