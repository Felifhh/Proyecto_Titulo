from django.db import migrations
from django.utils import timezone
from datetime import timezone as dt_timezone  # ← IMPORTANTE

def fix_naive_datetimes(apps, schema_editor):
    Auditoria = apps.get_model("Auditoria", "Auditoria")

    for row in Auditoria.objects.all():
        fecha = row.fecha_evento

        # Si es naive (sin timezone)
        if fecha and timezone.is_naive(fecha):
            # Interpretarlo como UTC correctamente
            aware_fecha = fecha.replace(tzinfo=dt_timezone.utc)

            row.fecha_evento = aware_fecha
            row.save(update_fields=["fecha_evento"])


class Migration(migrations.Migration):

    dependencies = [
        ('Auditoria', '0001_initial'),  # Ajusta según tu última migración
    ]

    operations = [
        migrations.RunPython(fix_naive_datetimes),
    ]

