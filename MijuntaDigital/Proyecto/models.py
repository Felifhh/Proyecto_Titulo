from django.db import models


class Proyecto(models.Model):
    id_proyecto = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Usuarios.Vecino', models.DO_NOTHING, db_column='id_vecino')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    documento_adj = models.CharField(max_length=255, blank=True, null=True)
    fecha_postulacion = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=11, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proyecto'

