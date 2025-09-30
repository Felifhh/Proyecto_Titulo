# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Solicitud(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Usuarios.Vecino', models.DO_NOTHING, db_column='id_vecino')
    tipo = models.CharField(max_length=10, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=10, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'solicitud'
