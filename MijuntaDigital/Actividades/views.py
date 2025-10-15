from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from datetime import date
from .models import Actividad, InscripcionActividad
from .forms import ActividadForm
from Usuarios.models import Vecino
from datetime import datetime
from django.utils import timezone



def lista_actividades(request):
    # Finalizar automáticamente actividades vencidas
    ahora = timezone.now()
    for act in Actividad.objects.filter(estado="Activa"):
        fin = datetime.combine(act.fecha, act.hora_fin)
        if fin <= ahora.replace(tzinfo=None):
            act.estado = "Finalizada"
            act.save()

    estado_actual = request.GET.get("estado", "Activa")
    busqueda = request.GET.get("q", "")

    actividades = (
        Actividad.objects.annotate(inscritos=Count("inscripciones"))
        .filter(estado=estado_actual)
        .order_by("-fecha", "-hora_inicio")
    )

    if busqueda:
        actividades = actividades.filter(
            Q(titulo__icontains=busqueda) | Q(ubicacion__icontains=busqueda)
        )

    return render(
        request,
        "Actividades/lista.html",
        {"actividades": actividades, "estado_actual": estado_actual},
    )


def crear_actividad(request):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])

    # Verificar si ya tiene una actividad activa
    if Actividad.objects.filter(id_vecino=vecino, estado='Activa', fecha__gte=date.today()).exists():
        messages.warning(request, "Ya tienes una actividad activa. Debes finalizarla o cancelarla antes de crear otra.")
        return redirect("lista_actividades")

    if request.method == "POST":
        form = ActividadForm(request.POST, vecino=vecino)
        if form.is_valid():
            act = form.save(commit=False)
            act.id_vecino = vecino

            # Si quieres, puedes dejar este bloque por doble seguridad
            reserva = form.cleaned_data.get('vincular_reserva')
            if reserva:
                act.fecha = reserva.fecha
                act.hora_inicio = reserva.hora_inicio
                act.hora_fin = reserva.hora_fin

            act.save()
            messages.success(request, "Actividad creada correctamente.")
            return redirect("detalle_actividad", id_actividad=act.id_actividad)
    else:
        form = ActividadForm(vecino=vecino)

    return render(request, "Actividades/crear.html", {"form": form})

def cancelar_actividad(request, id_actividad):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])
    act = get_object_or_404(Actividad, pk=id_actividad)

    # Solo el creador puede cancelarla
    if act.id_vecino_id != vecino.id_vecino:
        messages.error(request, "Solo el creador puede cancelar la actividad.")
        return redirect("detalle_actividad", id_actividad=id_actividad)

    # Solo actividades activas se pueden cancelar
    if act.estado != "Activa":
        messages.info(request, "Solo las actividades activas pueden ser canceladas.")
        return redirect("detalle_actividad", id_actividad=id_actividad)

    act.estado = "Cancelada"
    act.save()
    messages.warning(request, "Actividad cancelada correctamente.")
    return redirect("lista_actividades")



def detalle_actividad(request, id_actividad):
    act = get_object_or_404(Actividad, pk=id_actividad)

    # --- AUTO FINALIZACIÓN ---
    ahora = timezone.now()
    fin_actividad = datetime.combine(act.fecha, act.hora_fin)

    # Si ya pasó la hora de término y sigue activa → finaliza automáticamente
    if act.estado == "Activa" and fin_actividad <= ahora.replace(tzinfo=None):
        act.estado = "Finalizada"
        act.save()

    inscritos = act.inscripciones.count()
    disponibles = max(0, (act.cupos or 0) - inscritos)
    return render(request, "Actividades/detalle.html", {
        "actividad": act,
        "inscritos": inscritos,
        "disponibles": disponibles
    })


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
        messages.success(request, "Inscripción realizada correctamente.")
    else:
        messages.info(request, "Ya estabas inscrito.")
    return redirect("detalle_actividad", id_actividad=id_actividad)


def cancelar_inscripcion(request, id_actividad):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])
    act = get_object_or_404(Actividad, pk=id_actividad)
    InscripcionActividad.objects.filter(id_actividad=act, id_vecino=vecino).delete()
    messages.info(request, "Inscripción cancelada.")
    return redirect("detalle_actividad", id_actividad=id_actividad)


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
    messages.success(request, "Actividad finalizada correctamente.")
    return redirect("lista_actividades")



def home(request):
    actividades_recientes = (
        Actividad.objects
        .filter(estado__iexact="Activa")  
        .annotate(inscritos=Count("inscripciones"))
        .order_by("-id_actividad")[:3]
    )
    return render(request, "home.html", {"actividades_recientes": actividades_recientes})
