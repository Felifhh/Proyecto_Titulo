# ==============================================
# IMPORTACIONES
# ==============================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q
from Usuarios.decorators import require_role
from Notificaciones.models import Notificacion
from .models import Solicitud
from Usuarios.models import Vecino
from Auditoria.utils import registrar_evento  #  Integración de auditoría


# ==============================================
# CREAR SOLICITUD (Vecinos)
# ==============================================
@require_http_methods(["GET", "POST"])
@require_role(["vecino", "presidente", "secretario", "tesorero"])
def crear_solicitud(request):
    """
    Permite a un vecino crear una nueva solicitud ciudadana.
    Las solicitudes se crean en estado 'Pendiente'.
    """
    vecino_id = request.session.get("vecino_id")

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        descripcion = request.POST.get("descripcion")

        Solicitud.objects.create(
            id_vecino_id=vecino_id,
            tipo=tipo,
            descripcion=descripcion,
            estado="Pendiente"
        )

        # 🔹 Auditoría
        registrar_evento(request, f"Creación de solicitud ciudadana tipo '{tipo}'", "Éxito")

        # Notificación al directorio
        Notificacion.objects.create(
            titulo="Nueva solicitud ciudadana",
            mensaje=f"Un vecino ha enviado una solicitud de tipo {tipo}.",
            tipo="directorio"
        )

        messages.success(request, "Tu solicitud ha sido enviada correctamente.")
        return redirect("mis_solicitudes")

    return render(request, "Solicitudes/crear_solicitud.html")


# ==============================================
# MIS SOLICITUDES (Vecinos)
# ==============================================
@require_role(["vecino", "presidente", "secretario", "tesorero"])
def mis_solicitudes(request):
    """
    Muestra todas las solicitudes realizadas por el vecino autenticado.
    """
    vecino_id = request.session.get("vecino_id")
    solicitudes = Solicitud.objects.filter(id_vecino=vecino_id).order_by("-fecha_creacion")

    return render(request, "Solicitudes/mis_solicitudes.html", {"solicitudes": solicitudes})


# ==============================================
# GESTIONAR SOLICITUDES (Directiva)
# ==============================================
@require_role(["presidente", "secretario", "tesorero"])
def gestionar_solicitudes(request):
    """
    Muestra todas las solicitudes ciudadanas (de todos los vecinos).
    Permite filtrar por estado y por búsqueda.
    """

    # Obtener estado desde la URL (default = Pendiente)
    estado_actual = request.GET.get("estado", "Pendiente")

    # Filtrar por estado
    solicitudes = Solicitud.objects.filter(estado=estado_actual).order_by("-fecha_creacion")

    # Buscador
    query = request.GET.get("buscar", "").strip()
    if query:
        solicitudes = solicitudes.filter(
            Q(tipo__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(id_vecino__nombre__icontains=query)
        )

    return render(request, "Solicitudes/gestionar_solicitudes.html", {
        "solicitudes": solicitudes,
        "query": query,
        "estado_actual": estado_actual,
    })



# ==============================================
# DETALLE DE SOLICITUD (Todos)
# ==============================================
@require_role(["vecino", "presidente", "secretario", "tesorero"])
def detalle_solicitud(request, id_solicitud):
    """
    Muestra el detalle completo de una solicitud ciudadana.
    """
    solicitud = get_object_or_404(Solicitud, pk=id_solicitud)
    return render(request, "Solicitudes/detalle_solicitud.html", {"solicitud": solicitud})


# ==============================================
# ACTUALIZAR ESTADO DE SOLICITUD (Directiva)
# ==============================================
@require_POST
@require_role(["presidente", "secretario", "tesorero"])
def actualizar_estado_solicitud(request, id_solicitud):
    """
    Permite al directorio actualizar el estado de una solicitud:
    Pendiente → En Proceso / Resuelta / Rechazada
    """
    solicitud = get_object_or_404(Solicitud, pk=id_solicitud)
    nuevo_estado = request.POST.get("estado")

    if nuevo_estado not in ["En Proceso", "Resuelta", "Rechazada"]:
        messages.error(request, "Estado no válido.")
        registrar_evento(request, f"Intento fallido de cambio de estado en solicitud {solicitud.id_solicitud}", "Estado inválido")
        return redirect("gestionar_solicitudes")

    solicitud.estado = nuevo_estado
    solicitud.save()

    # 🔹 Auditoría
    registrar_evento(request, f"Cambio de estado de solicitud #{solicitud.id_solicitud} a '{nuevo_estado}'", "Éxito")

    # Notificación para el vecino
    Notificacion.objects.create(
        titulo="Actualización de solicitud",
        mensaje=f"Tu solicitud de tipo {solicitud.tipo} fue marcada como '{nuevo_estado}'.",
        tipo="global"
    )

    messages.success(request, f"La solicitud fue actualizada a estado '{nuevo_estado}'.")
    return redirect("gestionar_solicitudes")
