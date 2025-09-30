# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Usuarios.Vecino', models.DO_NOTHING, db_column='id_vecino')
    espacio = models.CharField(max_length=100)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    moneda = models.CharField(max_length=3, blank=True, null=True)
    estado = models.CharField(max_length=10, blank=True, null=True)
    fecha_reserva = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reserva'
