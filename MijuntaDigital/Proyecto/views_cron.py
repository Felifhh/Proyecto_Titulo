from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Proyecto.utils import cerrar_votaciones_expiradas

@csrf_exempt
def cron_cerrar_votaciones(request):
    """
    Endpoint llamado por Supabase Cron Job.
    Ejecuta el cierre automático de votaciones.
    """
    cerrar_votaciones_expiradas()
    return JsonResponse({"status": "ok", "message": "Votaciones cerradas"})
