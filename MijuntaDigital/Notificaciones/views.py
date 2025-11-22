from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import NotificacionUsuario

@require_POST
def marcar_leida(request, notificacion_id):
    vecino_id = request.session.get('vecino_id')
    if not vecino_id:
        return JsonResponse({'ok': False, 'error': 'No autenticado'}, status=401)

    noti_user, _ = NotificacionUsuario.objects.get_or_create(
        id_vecino=vecino_id,
        notificacion_id=notificacion_id
    )
    noti_user.leida = True
    noti_user.save()
    return JsonResponse({'ok': True})

