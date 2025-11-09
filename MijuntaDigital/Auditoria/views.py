from datetime import datetime, date, timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib import messages
from django.db.models import Avg, Sum
from django.db.models.expressions import RawSQL
from collections import defaultdict
import json
import calendar
from django.core.serializers.json import DjangoJSONEncoder

from Auditoria.models import Auditoria, Metricas
from Usuarios.models import Vecino
from Actividades.models import Actividad
from Reserva.models import Reserva
from Certificados.models import Certificado
from pagos.models import Transaccion
from Auditoria.utils import actualizar_metricas_globales


def panel_auditoria(request):
    rol = request.session.get("vecino_rol", "").lower()
    if rol not in ["presidente", "secretario", "tesorero"]:
        messages.error(request, "No tienes permisos para acceder a la auditoría.")
        return render(request, "error_permisos.html")

    usuario_id = request.GET.get("usuario")
    fecha_str = request.GET.get("fecha")
    usuario_transaccion = request.GET.get("usuario_transaccion")
    fecha_transaccion = request.GET.get("fecha_transaccion")

    hoy = timezone.localdate()

    # Conversión de fechas
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else hoy
    except (ValueError, TypeError):
        fecha = hoy
    try:
        fecha_t = datetime.strptime(fecha_transaccion, "%Y-%m-%d").date() if fecha_transaccion else hoy
    except (ValueError, TypeError):
        fecha_t = hoy

    inicio_mes = datetime(fecha.year, fecha.month, 1)
    _, ultimo_dia = calendar.monthrange(fecha.year, fecha.month)
    fin_mes = datetime(fecha.year, fecha.month, ultimo_dia, 23, 59, 59)

    actualizar_metricas_globales()

    # ----------- AUDITORÍA -------------
    eventos = Auditoria.objects.select_related("id_vecino").filter(
        fecha_evento__range=(inicio_mes, fin_mes)
    ).order_by("-fecha_evento")

    if usuario_id and usuario_id not in ["todos", "None", "", None]:
        try:
            eventos = eventos.filter(id_vecino_id=int(usuario_id))
        except (ValueError, TypeError):
            pass


    paginator = Paginator(eventos, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ----------- TRANSACCIONES -------------
    inicio_dia_t = timezone.make_aware(datetime.combine(fecha_t, datetime.min.time()))
    fin_dia_t = timezone.make_aware(datetime.combine(fecha_t, datetime.max.time()))

    transacciones = Transaccion.objects.select_related("id_vecino").filter(
        fecha__range=(inicio_dia_t, fin_dia_t)
    ).order_by("-fecha")

    if usuario_transaccion and usuario_transaccion not in ["todos", "None", "", None]:
        try:
            transacciones = transacciones.filter(id_vecino_id=int(usuario_transaccion))
        except (ValueError, TypeError):
            pass


    paginator_t = Paginator(transacciones, 10)
    page_number_t = request.GET.get("page_t")
    page_obj_t = paginator_t.get_page(page_number_t)

    usuarios = Vecino.objects.filter(estado="Activo").order_by("nombre")

    # ----------- MÉTRICAS -------------
    dias_mes = [date(fecha.year, fecha.month, d) for d in range(1, ultimo_dia + 1)]
    etiquetas_dias = [d.strftime("%d") for d in dias_mes]

    metricas_diarias = (
        Metricas.objects
        .annotate(dia=RawSQL("DATE(fecha)", []))
        .values("dia", "descripcion")
        .annotate(valor_promedio=Avg("valor"))
        .filter(fecha__range=(inicio_mes, fin_mes))
        .order_by("dia")
    )

    metricas_grouped = defaultdict(lambda: {d.strftime("%d"): 0 for d in dias_mes})

    for m in metricas_diarias:
        try:
            dia_label = datetime.strptime(str(m["dia"]), "%Y-%m-%d").strftime("%d")
        except Exception:
            dia_label = str(m["dia"])
        metricas_grouped[m["descripcion"]][dia_label] = int(m["valor_promedio"] or 0)

    chart_series = []
    for descripcion, valores_por_dia in metricas_grouped.items():
        chart_series.append({
            "label": descripcion,
            "labels": etiquetas_dias,
            "data": [valores_por_dia.get(d, 0) for d in etiquetas_dias],
        })

    resumen = {
        "vecinos_activos": Vecino.objects.filter(estado="Activo").count(),
        "actividades_no_canceladas": Actividad.objects.exclude(estado="Cancelada").count(),
        "reservas_no_canceladas": Reserva.objects.exclude(estado="Cancelada").count(),
        "certificados_emitidos": Certificado.objects.filter(estado="Emitido").count(),
        "monto_recaudado": Transaccion.objects.filter(estado="Autorizada").aggregate(total=Sum("monto"))["total"] or 0,
    }

    context = {
        "page_obj": page_obj,
        "usuarios": usuarios,
        "usuario_id": usuario_id,
        "resumen": resumen,
        "fecha": fecha,
        "fecha_t": fecha_t,
        "usuario_transaccion": usuario_transaccion,
        "chart_series_json": json.dumps(chart_series, cls=DjangoJSONEncoder),
        "page_obj_t": page_obj_t,
        "dias_mes": etiquetas_dias,
        "hoy": hoy,
    }

    return render(request, "Auditoria/panel_auditoria.html", context)
