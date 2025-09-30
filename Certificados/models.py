# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Certificado(models.Model):
    id_certificado = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Usuarios.Vecino', models.DO_NOTHING, db_column='id_vecino')
    tipo = models.CharField(max_length=10, blank=True, null=True)
    fecha_emision = models.DateTimeField(blank=True, null=True)
    folio = models.CharField(unique=True, max_length=50, blank=True, null=True)
    qr_code = models.CharField(max_length=255, blank=True, null=True)
    firma_digital = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=9, blank=True, null=True)


    id_vecino = models.ForeignKey('Usuarios.Vecino', models.DO_NOTHING, db_column='id_vecino')


    class Meta:
        managed = False
        db_table = 'certificado'
