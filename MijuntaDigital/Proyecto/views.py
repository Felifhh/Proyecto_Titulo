# ==============================================
# IMPORTACIONES
# ==============================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from Auditoria.utils import registrar_evento  # Integración de auditoría

# Modelos
from .models import Proyecto, VotoProyecto
from Notificaciones.models import Notificacion

# Decorador personalizado (rol)
from Usuarios.decorators import require_role


# ==============================================
# MIS PROYECTOS (solo vecinos)
# ==============================================
@require_role(["presidente", "secretario", "tesorero", "vecino"])
def mis_proyectos(request):
    vecino_id = request.session.get("vecino_id")
    proyectos = Proyecto.objects.filter(id_vecino=vecino_id).order_by("-fecha_postulacion")
    return render(request, "Proyecto/mis_proyectos.html", {"proyectos": proyectos})



# ==============================================
# CREAR NUEVO PROYECTO
# ==============================================
@require_http_methods(["GET", "POST"])
@require_role(["presidente", "secretario", "tesorero", "vecino"])
def crear_proyecto(request):
    vecino_id = request.session.get("vecino_id")

    proyectos_activos = Proyecto.objects.filter(
        id_vecino=vecino_id,
        estado__in=["En Revisión", "En Votación"]
    )

    if proyectos_activos.exists():
        messages.warning(request, "Ya tienes un proyecto activo o pendiente.")
        return redirect("mis_proyectos")

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        presupuesto = request.POST.get("presupuesto")
        documento_adj = request.FILES.get("documento_adj")

        Proyecto.objects.create(
            id_vecino_id=vecino_id,
            titulo=titulo,
            descripcion=descripcion,
            presupuesto=presupuesto,
            documento_adj=documento_adj,
            estado="En Revisión",
            estado_votacion="En Espera de Votación"
        )

        # 🔹 Auditoría
        registrar_evento(request, f"Postulación del proyecto '{titulo}'", "Éxito")

        # Notificación al directorio
        Notificacion.objects.create(
            titulo="Nueva postulación de proyecto",
            mensaje=f"Un vecino ha postulado el proyecto '{titulo}'.",
            tipo="directorio"
        )

        messages.success(request, "Tu proyecto fue enviado correctamente.")
        return redirect("mis_proyectos")

    return render(request, "Proyecto/crear_proyecto.html")


# ==============================================
# GESTIONAR PROYECTOS (Directiva)
# ==============================================
@require_role(["presidente", "secretario", "tesorero"])
def gestionar_proyectos(request):
    proyectos = Proyecto.objects.filter(estado="En Revisión").order_by("-fecha_postulacion")
    query = request.GET.get("buscar", "").strip()
    if query:
        proyectos = proyectos.filter(Q(titulo__icontains=query) | Q(descripcion__icontains=query))
    return render(request, "Proyecto/gestionar_proyectos.html", {"proyectos": proyectos, "query": query})



# ==============================================
# APROBAR / RECHAZAR PROYECTO
# ==============================================
@require_POST
@require_role(['presidente', 'secretario', 'tesorero'])
def actualizar_estado_proyecto(request, id_proyecto, accion):
    proyecto = get_object_or_404(Proyecto, pk=id_proyecto)

    if accion == "aprobar":
        proyecto.estado = "En Votación"
        proyecto.fecha_inicio_votacion = timezone.now()
        proyecto.fecha_fin_votacion = timezone.now() + timedelta(days=15)
        proyecto.save()

        registrar_evento(request, f"Aprobación del proyecto '{proyecto.titulo}'", "Éxito")

        Notificacion.objects.create(
            titulo="Nuevo proyecto en votación",
            mensaje=f"El proyecto '{proyecto.titulo}' ha sido aprobado y está disponible para votación.",
            tipo="global"
        )
        messages.success(request, f"El proyecto '{proyecto.titulo}' fue aprobado y se encuentra en votación.")

    elif accion == "rechazar":
        proyecto.estado = "Rechazado"
        proyecto.save()

        registrar_evento(request, f"Rechazo del proyecto '{proyecto.titulo}'", "Éxito")

        Notificacion.objects.create(
            titulo="Proyecto rechazado",
            mensaje=f"El proyecto '{proyecto.titulo}' fue rechazado por la directiva.",
            tipo="directorio"
        )
        messages.warning(request, f"El proyecto '{proyecto.titulo}' fue rechazado correctamente.")
    else:
        registrar_evento(request, f"Intento de cambio de estado inválido para proyecto '{proyecto.titulo}'", "Error")
        messages.error(request, "Acción no válida.")

    return redirect("gestionar_proyectos")



# ==============================================
# PROYECTOS EN VOTACIÓN / FINALIZADOS
# ==============================================
@require_role(["presidente", "secretario", "tesorero", "vecino"])
def proyectos_votacion(request):
    """
    Muestra todos los proyectos en votación o finalizados.
    Visible para todos los vecinos.
    """
    proyectos = Proyecto.objects.filter(
        estado__in=["En Votación", "Finalizado"]
    ).order_by("-fecha_postulacion")

    return render(request, "Proyecto/proyectos_votacion.html", {
        "proyectos": proyectos
    })


# ==============================================
# DETALLE DEL PROYECTO GENERAL
# ==============================================
@require_role(["presidente", "secretario", "tesorero", "vecino"])
def detalle_proyecto(request, id_proyecto):
    """
    Muestra información completa del proyecto seleccionado.
    Incluye votos actuales si está en votación.
    """
    proyecto = get_object_or_404(Proyecto, pk=id_proyecto)
    votos_a_favor = VotoProyecto.objects.filter(id_proyecto=proyecto, voto=True).count()
    votos_en_contra = VotoProyecto.objects.filter(id_proyecto=proyecto, voto=False).count()
    ya_voto = False

    if request.session.get("vecino_id"):
        vecino_id = request.session["vecino_id"]
        ya_voto = VotoProyecto.objects.filter(id_proyecto=proyecto, id_vecino_id=vecino_id).exists()

    return render(request, "Proyecto/detalle_proyecto.html", {
        "proyecto": proyecto,
        "votos_a_favor": votos_a_favor,
        "votos_en_contra": votos_en_contra,
        "ya_voto": ya_voto
    })


# ==============================================
# VOTAR POR UN PROYECTO
# ==============================================
@require_role(["vecino", "presidente", "secretario", "tesorero"])
def votar_proyecto(request, id_proyecto, decision):
    """
    Permite a un vecino emitir su voto a favor o en contra de un proyecto.
    Solo puede votar una vez por proyecto.
    """
    vecino_id = request.session.get("vecino_id")
    proyecto = get_object_or_404(Proyecto, pk=id_proyecto)

    # Verifica si aún está en votación
    if proyecto.estado != "En Votación":
        messages.warning(request, "Este proyecto ya no está en votación.")
        return redirect("proyectos_votacion")

    if proyecto.fecha_fin_votacion and timezone.now() > proyecto.fecha_fin_votacion:
        messages.warning(request, "La votación ha finalizado para este proyecto.")
        return redirect("proyectos_votacion")

    # Evita doble voto
    if VotoProyecto.objects.filter(id_proyecto=proyecto, id_vecino_id=vecino_id).exists():
        messages.error(request, "Ya has votado en este proyecto.")
        return redirect("detalle_proyecto", id_proyecto=proyecto.id_proyecto)

    # Registra el voto
    voto_a_favor = (decision == "favor")
    VotoProyecto.objects.create(
        id_proyecto=proyecto,
        id_vecino_id=vecino_id,
        voto=voto_a_favor
    )

    messages.success(request, f"Tu voto {'a favor' if voto_a_favor else 'en contra'} fue registrado correctamente.")
    return redirect("detalle_proyecto", id_proyecto=proyecto.id_proyecto)


# ==============================================
# CIERRE AUTOMÁTICO DE VOTACIONES
# ==============================================
def cerrar_votaciones_expiradas():
    """
    Cierra automáticamente los proyectos cuya fecha_fin_votacion ya venció.
    """
    hoy = timezone.now()
    expirados = Proyecto.objects.filter(estado="En Votación", fecha_fin_votacion__lt=hoy)

    for proyecto in expirados:
        votos_a_favor = VotoProyecto.objects.filter(id_proyecto=proyecto, voto=True).count()
        votos_en_contra = VotoProyecto.objects.filter(id_proyecto=proyecto, voto=False).count()

        proyecto.estado_votacion = "Aprobado por Votación" if votos_a_favor > votos_en_contra else "Rechazado por Votación"
        proyecto.estado = "Finalizado"
        proyecto.save()

        # 🔹 Auditoría
        registrar_evento(None, f"Cierre automático del proyecto '{proyecto.titulo}'", "Finalizado")



# ==============================================
# PÁGINA DE INICIO DEL MÓDULO DE PROYECTOS
# ==============================================
@require_role(["presidente", "secretario", "tesorero", "vecino"])
def proyectos_inicio(request):
    """
    Vista principal del módulo de proyectos vecinales.
    Muestra acceso directo a 'Mis Proyectos' y 'Proyectos en Votación'.
    """
    return render(request, "Proyecto/proyectos_inicio.html")

# ==============================================
# DETALLE DE PROYECTO (VISIÓN DE DIRECTIVA)
# ==============================================
@require_role(["presidente", "secretario", "tesorero"])
def detalle_proyecto_directiva(request, id_proyecto):
    """
    Muestra el detalle completo de un proyecto enviado por un vecino.
    Solo accesible para el Directorio (Presidente, Secretario, Tesorero).
    Desde aquí se puede aprobar o rechazar el proyecto.
    """
    proyecto = get_object_or_404(Proyecto, pk=id_proyecto)

    # Si se envía un formulario (Aprobar o Rechazar)
    if request.method == "POST":
        accion = request.POST.get("accion")

        # Aprobar proyecto → pasa a "En Votación"
        if accion == "aprobar":
            proyecto.estado = "En Votación"
            proyecto.fecha_inicio_votacion = timezone.now()
            proyecto.fecha_fin_votacion = timezone.now() + timedelta(days=15)
            proyecto.save()

            Notificacion.objects.create(
                titulo="Nuevo proyecto en votación",
                mensaje=f"El proyecto '{proyecto.titulo}' ha sido aprobado y se encuentra disponible para votación vecinal.",
                tipo="global"
            )

            messages.success(request, f"El proyecto '{proyecto.titulo}' fue aprobado correctamente.")
            return redirect("gestionar_proyectos")

        # Rechazar proyecto → cambia a "Rechazado"
        elif accion == "rechazar":
            proyecto.estado = "Rechazado"
            proyecto.save()

            Notificacion.objects.create(
                titulo="Proyecto rechazado",
                mensaje=f"El proyecto '{proyecto.titulo}' fue rechazado por la directiva.",
                tipo="directorio"
            )

            messages.warning(request, f"El proyecto '{proyecto.titulo}' fue rechazado correctamente.")
            return redirect("gestionar_proyectos")

        # Acción inválida
        else:
            messages.error(request, "Acción no válida.")
            return redirect("gestionar_proyectos")

    # Renderiza la vista de detalle (GET)
    return render(request, "Proyecto/detalle_proyecto_directiva.html", {"proyecto": proyecto})
