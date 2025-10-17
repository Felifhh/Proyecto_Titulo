from django.db import models

class Actividad(models.Model):
    id_actividad = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Usuarios.Vecino', on_delete=models.CASCADE, db_column='id_vecino')
    titulo = models.CharField(max_length=200)
    ubicacion = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    cupos = models.IntegerField(blank=True, null=True)
    estado = models.CharField(
        max_length=15,
        choices=[('Activa', 'Activa'), ('Finalizada', 'Finalizada'), ('Cancelada', 'Cancelada')],
        default='Activa'
    )

    class Meta:
        db_table = 'actividad'
        managed = False

    def __str__(self):
        return self.titulo


class InscripcionActividad(models.Model):
    id_inscripcion = models.AutoField(primary_key=True)
    id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='id_actividad', related_name='inscripciones')
    id_vecino = models.ForeignKey('Usuarios.Vecino', on_delete=models.CASCADE, db_column='id_vecino')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inscripcion_actividad'
        managed = False
        unique_together = ('id_actividad', 'id_vecino')
