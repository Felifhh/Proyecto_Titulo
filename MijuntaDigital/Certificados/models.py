from django.db import models
from django.dispatch import receiver
import os


class Certificado(models.Model):
    id_certificado = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Usuarios.Vecino', models.DO_NOTHING, db_column='id_vecino')
    tipo = models.CharField(max_length=50, blank=True, null=True)
    fecha_emision = models.DateTimeField(blank=True, null=True)
    folio = models.CharField(unique=True, max_length=50, blank=True, null=True)
    qr_code = models.CharField(max_length=255, blank=True, null=True)  # 🔹 ruta del QR
    firma_digital = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'certificado'

    def __str__(self):
        return f"{self.tipo} - {self.id_vecino.nombre}"

    # eliminar el archivo QR antiguo al reemplazarlo
    def save(self, *args, **kwargs):
        try:
            old = Certificado.objects.get(pk=self.pk)
            # compara ruta anterior vs nueva
            if old.qr_code and old.qr_code != self.qr_code:
                old_path = old.qr_code.replace('/media/', '').replace('\\', '/')
                full_old_path = os.path.join('media', old_path)
                if os.path.isfile(full_old_path):
                    os.remove(full_old_path)
        except Certificado.DoesNotExist:
            pass
        super().save(*args, **kwargs)


# eliminar el QR del disco si se borra el certificado
@receiver(models.signals.post_delete, sender=Certificado)
def auto_delete_qr_on_delete(sender, instance, **kwargs):
    if instance.qr_code:
        path = instance.qr_code.replace('/media/', '').replace('\\', '/')
        full_path = os.path.join('media', path)
        if os.path.isfile(full_path):
            os.remove(full_path)

