# Proyecto/utils.py
from django.utils import timezone
from Auditoria.models import Auditoria
from Proyecto.models import Proyecto, VotoProyecto


# ==============================================
# REGISTRAR EVENTO EN AUDITORÍA
# ==============================================
def registrar_evento(request, accion, resultado):
    """
    Registra un evento en la tabla de auditoría.
    Si request es None, el evento se registra como 'Sistema'.
    """

    try:
        id_vecino = None

        # Si viene request y hay sesión, obtenemos el vecino
        if request and request.session.get("vecino_id"):
            id_vecino = request.session.get("vecino_id")

        Auditoria.objects.create(
            id_vecino_id=id_vecino,
            accion=accion,
            resultado=resultado,
            fecha_evento=timezone.now()  # aware datetime
        )

    except Exception as e:
        print(f"[ERROR] No se pudo registrar evento: {e}")


# ==============================================
# CIERRE AUTOMÁTICO DE VOTACIONES EXPIRADAS
# ==============================================
def cerrar_votaciones_expiradas():
    """
    Cierra automáticamente los proyectos cuya fecha_fin_votacion venció.
    Compatible con cron, APScheduler o ejecución manual.
    """
    ahora = timezone.now()

    expirados = Proyecto.objects.filter(
        estado="En Votación",
        fecha_fin_votacion__lt=ahora
    )

    for proyecto in expirados:

        # Contar votos
        votos_favor = VotoProyecto.objects.filter(
            id_proyecto=proyecto, voto=True
        ).count()

        votos_contra = VotoProyecto.objects.filter(
            id_proyecto=proyecto, voto=False
        ).count()

        # Determinar resultado
        if votos_favor > votos_contra:
            proyecto.estado_votacion = "Aprobado por Votación"
        else:
            proyecto.estado_votacion = "Rechazado por Votación"

        proyecto.estado = "Finalizado"
        proyecto.save()

        # Registrar en Auditoría
        registrar_evento(
            None,  # None = Sistema
            f"Cierre automático del proyecto '{proyecto.titulo}'",
            "Finalizado"
        )

    return len(expirados)
