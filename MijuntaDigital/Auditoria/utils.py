# Auditoria/utils.py
from Auditoria.models import Auditoria
from Auditoria.models import Metricas
from django.utils import timezone

from Usuarios.models import Vecino
from Actividades.models import Actividad
from Reserva.models import Reserva
from Certificados.models import Certificado

def registrar_evento(request, accion, resultado="Éxito"):
    """
    Registra un evento de auditoría en la tabla Auditoria.
    """
    try:
        vecino_id = request.session.get("vecino_id")
        Auditoria.objects.create(
            id_vecino_id=vecino_id,
            accion=accion,
            resultado=resultado,
            fecha_evento=timezone.now()
        )
    except Exception as e:
        print(f"[AUDITORIA ERROR] No se pudo registrar el evento: {e}")


def registrar_metrica(descripcion, valor):
    """
    Registra una métrica en la tabla 'metricas' con fecha actual.
    Si ya existe una con la misma descripción en el mismo día, la actualiza.
    """
    hoy = timezone.now().date()
    metrica, created = Metricas.objects.get_or_create(
        descripcion=descripcion,
        fecha__date=hoy,
        defaults={"valor": valor, "fecha": timezone.now()}
    )

    if not created:
        metrica.valor = valor
        metrica.fecha = timezone.now()
        metrica.save()


def actualizar_metricas_globales():
    """
    Actualiza las métricas principales del sistema en la tabla 'metricas'.
    """
    from Auditoria.utils import registrar_metrica

    registrar_metrica("Vecinos activos", Vecino.objects.filter(estado="Activo").count())
    registrar_metrica("Actividades", Actividad.objects.exclude(estado="Cancelada").count())
    registrar_metrica("Reservas", Reserva.objects.exclude(estado="Cancelada").count())
    registrar_metrica("Certificados emitidos", Certificado.objects.filter(estado="Emitido").count())