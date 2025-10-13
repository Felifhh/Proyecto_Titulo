from django.db import models
from django.dispatch import receiver
import os


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'rol'

    def __str__(self):
        return self.nombre


class Vecino(models.Model):
    id_vecino = models.AutoField(primary_key=True)
    run = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    correo = models.EmailField(unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    contrasena = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    id_rol = models.ForeignKey('Rol', on_delete=models.DO_NOTHING, db_column='id_rol')
    estado = models.CharField(max_length=15, default='Pendiente')
    foto = models.ImageField(upload_to='perfiles/', default='perfiles/default.png', blank=True, null=True)
    evidencia = models.FileField(upload_to='evidencias_vecinos/', null=True, blank=True)

    class Meta:
        managed = False  # ya existe en la base
        db_table = 'vecino'

    def __str__(self):
        return f"{self.nombre} ({self.run})"


# === Señales para eliminar archivos antiguos ===

# Eliminar la foto anterior si se cambia
@receiver(models.signals.pre_save, sender=Vecino)
def auto_delete_old_files_on_change(sender, instance, **kwargs):
    """Elimina archivos antiguos (foto/evidencia) al actualizar el registro."""
    if not instance.pk:
        return False

    try:
        old = Vecino.objects.get(pk=instance.pk)
    except Vecino.DoesNotExist:
        return False

    # Si cambió la foto, eliminar la anterior
    if old.foto and old.foto != instance.foto:
        if os.path.isfile(old.foto.path):
            os.remove(old.foto.path)

    # Si cambió la evidencia, eliminar la anterior
    if old.evidencia and old.evidencia != instance.evidencia:
        if os.path.isfile(old.evidencia.path):
            os.remove(old.evidencia.path)


# Eliminar los archivos al borrar el registro
@receiver(models.signals.post_delete, sender=Vecino)
def auto_delete_files_on_delete(sender, instance, **kwargs):
    """Elimina los archivos asociados al eliminar un vecino."""
    if instance.foto and os.path.isfile(instance.foto.path):
        os.remove(instance.foto.path)
    if instance.evidencia and os.path.isfile(instance.evidencia.path):
        os.remove(instance.evidencia.path)
