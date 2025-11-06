from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Usuarios.decorators import require_role
from .forms import EspacioForm
from datetime import datetime, timedelta, time
from django.utils.timezone import make_aware
from Usuarios.models import Vecino
from .models import Reserva, EspacioComunal
from .forms import ReservaForm
from django.views.decorators.clickjacking import xframe_options_exempt
import requests
from django.urls import reverse
from transbank.webpay.webpay_plus.transaction import Transaction
from Auditoria.utils import registrar_evento  #  Integración de auditoría

def notificar_n8n(evento, datos):
    webhook_url = "https://felifhh.app.n8n.cloud/webhook/evento-app"  # URL definitiva
    try:
        requests.post(webhook_url, json={"evento": evento, **datos}, timeout=5)
        print(f" Evento '{evento}' enviado correctamente a n8n.")
    except Exception as e:
        print(f" Error enviando evento a n8n: {e}")



# ==============================================
# GESTIÓN DE ESPACIOS (Directiva)
# ==============================================
@require_role(['presidente', 'secretario', 'tesorero'])
def gestionar_espacios(request):
    query = request.GET.get('buscar', '').strip()
    espacios_activos = EspacioComunal.objects.filter(estado="Activo")
    espacios_inactivos = EspacioComunal.objects.filter(estado="Inactivo")

    if query:
        espacios_activos = espacios_activos.filter(nombre__icontains=query)
        espacios_inactivos = espacios_inactivos.filter(nombre__icontains=query)

    return render(request, "Reserva/gestion_espacios.html", {
        "activos": espacios_activos.order_by("-fecha_creacion"),
        "inactivos": espacios_inactivos.order_by("-fecha_creacion"),
        "query": query,
    })

@require_role(['presidente', 'secretario', 'tesorero'])
def cambiar_estado_espacio(request, id_espacio):
    """Activa o inactiva un espacio comunal."""
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)
    espacio.estado = "Activo" if espacio.estado == "Inactivo" else "Inactivo"
    espacio.save()
    messages.info(request, f"El estado de {espacio.nombre} ha sido cambiado a {espacio.estado}.")
    return redirect("gestionar_espacios")

@require_role(['presidente', 'secretario', 'tesorero'])
def crear_espacio(request):
    """Crea un nuevo espacio comunal con imagen obligatoria."""
    if request.method == "POST":
        form = EspacioForm(request.POST, request.FILES)
        if form.is_valid():
            espacio = form.save()
            registrar_evento(request, f"Creación de espacio comunal '{espacio.nombre}'", "Éxito")
            messages.success(request, "Espacio comunal creado correctamente.")
            return redirect('gestionar_espacios')
        else:
            registrar_evento(request, "Intento fallido de creación de espacio", "Error")
            messages.error(request, "Revisa los datos ingresados.")
    else:
        form = EspacioForm()

    return render(request, "Reserva/crear_espacio.html", {"form": form, "modo": "crear"})


@require_role(['presidente', 'secretario', 'tesorero'])
def editar_espacio(request, id_espacio):
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)
    if request.method == 'POST':
        form = EspacioForm(request.POST, request.FILES, instance=espacio)
        if form.is_valid():
            form.save()
            registrar_evento(request, f"Modificación del espacio '{espacio.nombre}'", "Éxito")
            messages.success(request, f"El espacio '{espacio.nombre}' fue actualizado correctamente.")
            return redirect('gestionar_espacios')
        else:
            registrar_evento(request, f"Error al editar espacio '{espacio.nombre}'", "Error")
            messages.error(request, "Error en el formulario.")
    else:
        form = EspacioForm(instance=espacio)
    return render(request, 'Reserva/editar_espacio.html', {'form': form, 'modo': 'editar', 'espacio': espacio})


@require_role(['presidente', 'secretario', 'tesorero'])
def desactivar_espacio(request, id_espacio):
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)
    espacio.estado = 'Inactivo'
    espacio.save()
    registrar_evento(request, f"Desactivación del espacio '{espacio.nombre}'", "Éxito")
    messages.warning(request, f"El espacio '{espacio.nombre}' ha sido desactivado.")
    return redirect('gestionar_espacios')


@require_role(['presidente', 'secretario', 'tesorero'])
def activar_espacio(request, id_espacio):
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)
    espacio.estado = 'Activo'
    espacio.save()
    registrar_evento(request, f"Activación del espacio '{espacio.nombre}'", "Éxito")
    messages.success(request, f"El espacio '{espacio.nombre}' ha sido activado correctamente.")
    return redirect('gestionar_espacios')


@require_role(['presidente', 'secretario', 'tesorero'])
def eliminar_espacio(request, id_espacio):
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)
    nombre = espacio.nombre
    espacio.delete()
    registrar_evento(request, f"Eliminación definitiva del espacio '{nombre}'", "Éxito")
    messages.error(request, f"{nombre} ha sido eliminado permanentemente.")
    return redirect("gestionar_espacios")

# ==============================================
# RESERVAS DE VECINOS
# ==============================================
def mis_reservas(request):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión para ver tus reservas.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])
    reservas = Reserva.objects.filter(id_vecino=vecino).order_by('-fecha_creacion')
    return render(request, "Reserva/mis_reservas.html", {"reservas": reservas, "vecino": vecino})




def ver_espacios_comunales(request):
    """
    Muestra los espacios comunales activos disponibles para reserva.
    """
    espacios = EspacioComunal.objects.filter(estado="Activo").order_by("nombre")
    return render(request, "Reserva/ver_espacios.html", {"espacios": espacios})



def reservar_desde_catalogo(request, id_espacio):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión para reservar un espacio.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio, estado="Activo")

    if request.method == "POST":
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva_temp = form.save(commit=False)
            total = espacio.monto_hora * (reserva_temp.hora_fin.hour - reserva_temp.hora_inicio.hour)

            # Auditoría: intento de reserva
            registrar_evento(request, f"Reserva solicitada para '{espacio.nombre}' el {reserva_temp.fecha}", "Pendiente de pago")

            buy_order = f"RSV-{vecino.id_vecino}-{int(timezone.now().timestamp())}"
            session_id = request.session.session_key or str(vecino.id_vecino)
            return_url = request.build_absolute_uri(reverse("retorno_pago_reserva"))

            tx = Transaction()
            tx.configure_for_testing()
            response = tx.create(buy_order, session_id, total, return_url)

            request.session["reserva_pago"] = {
                "vecino_id": vecino.id_vecino,
                "espacio_id": espacio.id_espacio,
                "fecha": str(reserva_temp.fecha),
                "hora_inicio": reserva_temp.hora_inicio.strftime("%H:%M"),
                "hora_fin": reserva_temp.hora_fin.strftime("%H:%M"),
                "total": total,
            }

            return render(request, "pagos/iniciar_pago.html", {"url": response["url"], "token": response["token"]})
        else:
            registrar_evento(request, f"Error en intento de reserva para '{espacio.nombre}'", "Formulario inválido")
            messages.error(request, "Hay errores en el formulario.")
    else:
        form = ReservaForm(initial={"id_espacio": espacio})
        if "id_espacio" in form.fields:
            form.fields["id_espacio"].disabled = True

    return render(request, "Reserva/reservar_desde_catalogo.html", {"form": form, "espacio": espacio})




def ver_disponibilidad(request, id_espacio):

    """
    Muestra los bloques horarios de un espacio comunal en una fecha.
    """
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)
    fecha_str = request.GET.get("fecha")
    
    # Si no se selecciona fecha, usar hoy
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else datetime.today().date()

    # Bloques horarios base (por ejemplo de 8:00 a 20:00)
    hora_inicio_dia = time(8, 0)
    hora_fin_dia = time(20, 0)
    intervalo = 60  # minutos por bloque
    bloques = []

    # Obtener reservas del día
    reservas = Reserva.objects.filter(
        id_espacio=espacio,
        fecha=fecha,
        estado__in=["Activa"]
    )

    hora_actual = datetime.combine(fecha, hora_inicio_dia)
    fin_dia = datetime.combine(fecha, hora_fin_dia)

    while hora_actual < fin_dia:
        siguiente = hora_actual + timedelta(minutes=intervalo)
        ocupado = reservas.filter(
            hora_inicio__lt=siguiente.time(),
            hora_fin__gt=hora_actual.time()
        ).exists()

        bloques.append({
            "inicio": hora_actual.strftime("%H:%M"),
            "fin": siguiente.strftime("%H:%M"),
            "estado": "Ocupado" if ocupado else "Libre"
        })

        hora_actual = siguiente

    return render(request, "Reserva/disponibilidad.html", {
        "espacio": espacio,
        "fecha": fecha,
        "bloques": bloques
    })



