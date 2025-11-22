from django.db import models

class Noticia(models.Model):
    id_noticia = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Usuarios.Vecino', models.DO_NOTHING, db_column='id_vecino')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='noticias/', blank=True, null=True)
    link = models.URLField(max_length=300, blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'noticia'

    def __str__(self):
        return self.titulo
