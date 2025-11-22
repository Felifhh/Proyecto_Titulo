from django.db import models
from Usuarios.models import Vecino

class Transaccion(models.Model):


    id_transaccion = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey(Vecino, on_delete=models.CASCADE, db_column='id_vecino', null=True)
    token = models.CharField(max_length=100)
    orden_compra = models.CharField(max_length=50)
    monto = models.IntegerField()
    estado =  models.CharField(max_length=20)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'transaccion'
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'

    def __str__(self):
        return f"{self.orden_compra} - {self.estado} - ${self.monto}"
