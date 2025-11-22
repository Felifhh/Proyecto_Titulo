# models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Proyecto(models.Model):
    ESTADOS_ADMIN = [
        ('En Revisión', 'En Revisión'),
        ('En Votación', 'En Votación'),
        ('Rechazado', 'Rechazado'),
        ('Finalizado', 'Finalizado'),
    ]

    ESTADOS_VOTACION = [
        ('En Espera de Votación', 'En Espera de Votación'),
        ('Aprobado por Votación', 'Aprobado por Votación'),
        ('Rechazado por Votación', 'Rechazado por Votación'),
    ]

    id_proyecto = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Usuarios.Vecino', models.DO_NOTHING, db_column='id_vecino')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    documento_adj = models.FileField(upload_to='proyectos/', null=True, blank=True)
    fecha_postulacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADOS_ADMIN, default='En Revisión')
    estado_votacion = models.CharField(max_length=25, choices=ESTADOS_VOTACION, default='En Espera de Votación')
    fecha_inicio_votacion = models.DateTimeField(blank=True, null=True)
    fecha_fin_votacion = models.DateTimeField(blank=True, null=True)

    def iniciar_votacion(self):
        """Activa la votación por 15 días."""
        self.estado = "En Votación"
        self.fecha_inicio_votacion = timezone.now()
        self.fecha_fin_votacion = self.fecha_inicio_votacion + timedelta(days=15)
        self.save()

    def finalizar_votacion(self):
        """Evalúa los votos y determina el resultado."""
        votos_a_favor = VotoProyecto.objects.filter(id_proyecto=self, voto=True).count()
        votos_en_contra = VotoProyecto.objects.filter(id_proyecto=self, voto=False).count()

        if votos_a_favor > votos_en_contra:
            self.estado_votacion = "Aprobado por Votación"
        else:
            self.estado_votacion = "Rechazado por Votación"

        self.estado = "Finalizado"
        self.save()

    class Meta:
        db_table = 'proyecto'


class VotoProyecto(models.Model):
    id_voto = models.AutoField(primary_key=True)
    id_proyecto = models.ForeignKey(Proyecto, models.CASCADE, db_column='id_proyecto')
    id_vecino = models.ForeignKey('Usuarios.Vecino', models.CASCADE, db_column='id_vecino')
    voto = models.BooleanField()  # True = a favor, False = en contra
    fecha_voto = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'voto_proyecto'
        unique_together = ('id_proyecto', 'id_vecino')


