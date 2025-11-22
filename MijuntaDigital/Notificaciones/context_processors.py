from .models import Notificacion, NotificacionUsuario

def notificaciones_context(request):
    """
    Inyecta las notificaciones y su conteo en todas las plantillas,
    compatible con versiones antiguas de MariaDB (sin subquery LIMIT).
    """
    ctx = {'notificaciones': [], 'notificaciones_no_leidas': []}

    # Solo si el usuario está logueado (usa sesión de vecino)
    if not request.session.get('vecino_id'):
        return ctx

    vecino_id = request.session['vecino_id']
    rol = (request.session.get('vecino_rol') or '').lower()

    # Filtro según tipo de usuario
    if rol in ['presidente', 'secretario', 'tesorero']:
        base = Notificacion.objects.filter(tipo__in=['global', 'directorio'])
    else:
        base = Notificacion.objects.filter(tipo='global')

    # 🔹 Evalúa los IDs primero para evitar el LIMIT dentro del IN (incompatible con MariaDB <10.6)
    notis = list(base.order_by('-fecha')[:15])
    notis_ids = [n.id_notificacion for n in notis]

    # 🔹 Recupera los estados de lectura usando los IDs directos
    leidas_map = {
        nu.notificacion_id: nu.leida
        for nu in NotificacionUsuario.objects.filter(
            id_vecino=vecino_id,
            notificacion_id__in=notis_ids
        )
    }

    # 🔹 Genera lista de no leídas
    no_leidas = [n for n in notis if not leidas_map.get(n.id_notificacion, False)]

    ctx['notificaciones'] = notis
    ctx['notificaciones_no_leidas'] = no_leidas
    return ctx

