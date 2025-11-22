# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Auditoria(models.Model):
    id_evento = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Usuarios.Vecino', models.DO_NOTHING, db_column='id_vecino')
    accion = models.CharField(max_length=255)
    fecha_evento = models.DateTimeField(auto_now_add=True)
    resultado = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auditoria'


class Metricas(models.Model):
    id_metrica = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    valor = models.IntegerField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'metricas'

