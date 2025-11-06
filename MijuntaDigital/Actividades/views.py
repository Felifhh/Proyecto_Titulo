from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date

from Auditoria.utils import registrar_evento
from Noticia.models import Noticia
from .models import Actividad, InscripcionActividad
from .forms import ActividadForm
from Usuarios.models import Vecino
from datetime import datetime
from django.utils import timezone



# ==============================================
# LISTAR ACTIVIDADES
# ==============================================
def lista_actividades(request):
    ahora = timezone.now()

    # Auto-finalización de actividades vencidas
    for act in Actividad.objects.filter(estado="Activa"):
        fin = datetime.combine(act.fecha, act.hora_fin)
        if fin <= ahora.replace(tzinfo=None):
            act.estado = "Finalizada"
            act.save()
            registrar_evento(None, f"Finalización automática de actividad '{act.titulo}'", "Sistema")

    estado_actual = request.GET.get("estado", "Activa")
    busqueda = request.GET.get("q", "")

    actividades = (
        Actividad.objects.annotate(inscritos=Count("inscripciones"))
        .filter(estado=estado_actual)
        .order_by("-fecha", "-hora_inicio")
    )

    if busqueda:
        actividades = actividades.filter(Q(titulo__icontains=busqueda) | Q(descripcion__icontains=busqueda))

    return render(
        request,
        "Actividades/lista.html",
        {"actividades": actividades, "estado_actual": estado_actual},
    )


# ==============================================
# CREAR NUEVA ACTIVIDAD
# ==============================================
def crear_actividad(request):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])

    # Evita más de una actividad activa
    if Actividad.objects.filter(id_vecino=vecino, estado='Activa', fecha__gte=date.today()).exists():
        messages.warning(request, "Ya tienes una actividad activa.")
        return redirect("lista_actividades")

    if request.method == "POST":
        form = ActividadForm(request.POST, vecino=vecino)
        if form.is_valid():
            act = form.save(commit=False)
            act.id_vecino = vecino
            act.save()
            registrar_evento(request, f"Creación de actividad '{act.titulo}'", "Éxito")
            messages.success(request, "Actividad creada correctamente.")
            return redirect("detalle_actividad", id_actividad=act.id_actividad)
        else:
            registrar_evento(request, "Intento fallido de creación de actividad", "Error")
    else:
        form = ActividadForm(vecino=vecino)

    return render(request, "Actividades/crear.html", {"form": form})


# ==============================================
# CANCELAR ACTIVIDAD
# ==============================================
def cancelar_actividad(request, id_actividad):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])
    act = get_object_or_404(Actividad, pk=id_actividad)

    if act.id_vecino_id != vecino.id_vecino:
        messages.error(request, "Solo el creador puede cancelar la actividad.")
        return redirect("detalle_actividad", id_actividad=id_actividad)

    if act.estado != "Activa":
        messages.info(request, "Solo las actividades activas pueden ser canceladas.")
        return redirect("detalle_actividad", id_actividad=id_actividad)

    act.estado = "Cancelada"
    act.save()
    registrar_evento(request, f"Cancelación de actividad '{act.titulo}'", "Éxito")
    messages.warning(request, "Actividad cancelada correctamente.")
    return redirect("lista_actividades")



# ==============================================
# DETALLE DE ACTIVIDAD
# ==============================================
def detalle_actividad(request, id_actividad):
    act = get_object_or_404(Actividad, pk=id_actividad)
    ahora = timezone.now()
    fin_actividad = datetime.combine(act.fecha, act.hora_fin)

    # Finalización automática
    if act.estado == "Activa" and fin_actividad <= ahora.replace(tzinfo=None):
        act.estado = "Finalizada"
        act.save()
        registrar_evento(None, f"Finalización automática de actividad '{act.titulo}'", "Sistema")

    inscritos = act.inscripciones.count()
    disponibles = max(0, (act.cupos or 0) - inscritos)

    # ✅ Verificar si el vecino está inscrito
    esta_inscrito = False
    if request.session.get("vecino_id"):
        vecino_id = request.session["vecino_id"]
        esta_inscrito = act.inscripciones.filter(id_vecino_id=vecino_id).exists()

    return render(request, "Actividades/detalle.html", {
        "actividad": act,
        "inscritos": inscritos,
        "disponibles": disponibles,
        "esta_inscrito": esta_inscrito,
    })

# ==============================================
# INSCRIBIRSE A UNA ACTIVIDAD
# ==============================================
def inscribirse_actividad(request, id_actividad):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])
    act = get_object_or_404(Actividad, pk=id_actividad)

    if act.id_vecino_id == vecino.id_vecino:
        messages.error(request, "No puedes inscribirte en tu propia actividad.")
        return redirect("detalle_actividad", id_actividad=id_actividad)

    if act.estado != 'Activa':
        messages.error(request, "Esta actividad no está activa.")
        return redirect("detalle_actividad", id_actividad=id_actividad)

    inscritos = act.inscripciones.count()
    if act.cupos and inscritos >= act.cupos:
        messages.error(request, "No quedan cupos disponibles.")
        return redirect("detalle_actividad", id_actividad=id_actividad)

    _, created = InscripcionActividad.objects.get_or_create(id_actividad=act, id_vecino=vecino)
    if created:
        registrar_evento(request, f"Inscripción en actividad '{act.titulo}'", "Éxito")
        messages.success(request, "Inscripción realizada correctamente.")
    else:
        registrar_evento(request, f"Intento de reinscripción en actividad '{act.titulo}'", "Rechazado")
        messages.info(request, "Ya estabas inscrito.")
    return redirect("detalle_actividad", id_actividad=id_actividad)



# ==============================================
# CANCELAR INSCRIPCIÓN
# ==============================================
def cancelar_inscripcion(request, id_actividad):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])
    act = get_object_or_404(Actividad, pk=id_actividad)

    InscripcionActividad.objects.filter(id_actividad=act, id_vecino=vecino).delete()
    registrar_evento(request, f"Cancelación de inscripción en actividad '{act.titulo}'", "Éxito")
    messages.info(request, "Inscripción cancelada correctamente.")
    return redirect("detalle_actividad", id_actividad=id_actividad)


# ==============================================
# FINALIZAR ACTIVIDAD (manual)
# ==============================================
def finalizar_actividad(request, id_actividad):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])
    act = get_object_or_404(Actividad, pk=id_actividad)

    if act.id_vecino_id != vecino.id_vecino:
        messages.error(request, "Solo el creador puede finalizar la actividad.")
        return redirect("detalle_actividad", id_actividad=id_actividad)

    act.estado = "Finalizada"
    act.save()
    registrar_evento(request, f"Finalización manual de actividad '{act.titulo}'", "Éxito")
    messages.success(request, "Actividad finalizada correctamente.")
    return redirect("lista_actividades")



# ==============================================
# HOME (muestra noticias y actividades recientes)
# ==============================================
def home(request):
    """
    Página principal que muestra noticias y actividades recientes.
    """
    # Últimas 3 noticias publicadas
    noticias_recientes = (
        Noticia.objects
        .all()
        .order_by("-fecha_publicacion")[:3]
    )

    actividades_recientes = (
        Actividad.objects
        .filter(estado__iexact="Activa")  
        .annotate(inscritos=Count("inscripciones"))
        .order_by("-id_actividad")[:3]
    )
    return render(request, "home.html", {
        "noticias_recientes": noticias_recientes,
        "actividades_recientes": actividades_recientes,
    })

