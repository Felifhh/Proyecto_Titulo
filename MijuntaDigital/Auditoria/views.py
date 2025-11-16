from datetime import datetime, date, timedelta
from django.http import HttpResponse, FileResponse
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
import requests

from .graficos import generar_grafico_semanal

import base64

def cargar_imagen_base64(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")



# ==============================================================
#  NOTIFICAR N8N
# ==============================================================

def notificar_n8n(evento, datos):
    webhook_url = "https://felifhhh.app.n8n.cloud/webhook/a2455f35-9e3c-4833-91d5-bfbc40ca9cb6"
    print("ENVIANDO A N8N:", webhook_url)
    try:
        requests.post(webhook_url, json={"evento": evento, **datos}, timeout=5)
        print(f"[OK] Evento '{evento}' enviado a n8n")
    except Exception as e:
        print(f"[ERROR] n8n: {e}")


# ==============================================================
#  PANEL PRINCIPAL DE AUDITORÍA
# ==============================================================

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

    # ---------------------------
    # FECHAS AUDITORÍA
    # ---------------------------
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else hoy
    except:
        fecha = hoy

    # ---------------------------
    # FECHAS TRANSACCIONES
    # ---------------------------
    if fecha_transaccion:
        try:
            fecha_t = datetime.strptime(fecha_transaccion, "%Y-%m-%d").date()
        except:
            fecha_t = None
    else:
        fecha_t = None

    inicio_mes = datetime(fecha.year, fecha.month, 1)
    _, ultimo_dia = calendar.monthrange(fecha.year, fecha.month)
    fin_mes = datetime(fecha.year, fecha.month, ultimo_dia, 23, 59, 59)

    actualizar_metricas_globales()

    # ==============================================================
    #  AUDITORÍA (POR DÍA O POR MES)
    # ==============================================================

    if fecha_str:
        inicio_dia = timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
        fin_dia = timezone.make_aware(datetime.combine(fecha, datetime.max.time()))

        eventos = Auditoria.objects.filter(fecha_evento__range=(inicio_dia, fin_dia))
    else:
        eventos = Auditoria.objects.filter(fecha_evento__range=(inicio_mes, fin_mes))

    if usuario_id and usuario_id not in ["todos", "", "None", None]:
        try:
            eventos = eventos.filter(id_vecino_id=int(usuario_id))
        except ValueError:
            pass  # ignora si el valor no es válido


    eventos = eventos.order_by("-fecha_evento")
    paginator = Paginator(eventos, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    # ==============================================================
    #  TRANSACCIONES
    # ==============================================================

    transacciones = Transaccion.objects.select_related("id_vecino").order_by("-fecha")

    if fecha_t:
        inicio_t = timezone.make_aware(datetime.combine(fecha_t, datetime.min.time()))
        fin_t = timezone.make_aware(datetime.combine(fecha_t, datetime.max.time()))
        transacciones = transacciones.filter(fecha__range=(inicio_t, fin_t))

    if usuario_transaccion and usuario_transaccion not in ["todos", "", None]:
        transacciones = transacciones.filter(id_vecino_id=int(usuario_transaccion))

    paginator_t = Paginator(transacciones, 10)
    page_obj_t = paginator_t.get_page(request.GET.get("page_t"))

    usuarios = Vecino.objects.filter(estado="Activo").order_by("nombre")

    # ==============================================================
    #  MÉTRICAS DIARIAS
    # ==============================================================

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
            dia_str = datetime.strptime(str(m["dia"]), "%Y-%m-%d").strftime("%d")
        except:
            dia_str = str(m["dia"])
        metricas_grouped[m["descripcion"]][dia_str] = int(m["valor_promedio"] or 0)

    chart_series = [
        {
            "label": descripcion,
            "labels": etiquetas_dias,
            "data": [valores[d] for d in etiquetas_dias],
        }
        for descripcion, valores in metricas_grouped.items()
    ]

    # ==============================================================
    #  RESUMEN GENERAL
    # ==============================================================

    resumen = {
        "vecinos_activos": usuarios.count(),
        "actividades_no_canceladas": Actividad.objects.exclude(estado="Cancelada").count(),
        "reservas_no_canceladas": Reserva.objects.exclude(estado="Cancelada").count(),
        "certificados_emitidos": Certificado.objects.filter(estado="Emitido").count(),
        "monto_recaudado": Transaccion.objects.filter(estado="Authorized").aggregate(total=Sum("monto"))["total"] or 0,
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
        "active_tab": request.GET.get("active_tab", "auditoria"),
    }

    return render(request, "Auditoria/panel_auditoria.html", context)


# ==============================================================
#  DESCARGAR PDF + ENVIAR DATOS A IA
# ==============================================================
from django.shortcuts import redirect

def descargar_reporte_pdf(request):
    """
    Genera el reporte, lo envía a n8n y muestra un mensaje flash.
    NO descarga PDF ni redirige fuera del panel.
    """

    hoy = timezone.now()
    inicio = hoy - timedelta(days=7)       
    inicio_pasada = hoy - timedelta(days=14)

    # ==============================
    #  TRANSACCIONES
    # ==============================
    transacciones_actuales = Transaccion.objects.filter(
        fecha__gte=inicio,
        estado="Authorized"
    )
    total_recaudado = transacciones_actuales.aggregate(total=Sum("monto"))["total"] or 0
    trans_sem = transacciones_actuales.count()

    transacciones_pasadas = Transaccion.objects.filter(
        fecha__gte=inicio_pasada,
        fecha__lt=inicio,
        estado="Authorized"
    )
    trans_sem_pas = transacciones_pasadas.count()

    # ==============================
    #  CERTIFICADOS
    # ==============================
    certificados_semana = Certificado.objects.filter(
        fecha_emision__gte=inicio
    ).count()

    certificados_pasados = Certificado.objects.filter(
        fecha_emision__gte=inicio_pasada,
        fecha_emision__lt=inicio
    ).count()

    # ==============================
    #  RESERVAS
    # ==============================
    reservas_semana = Reserva.objects.filter(
        fecha__gte=inicio,
        estado="Activa"
    ).count()

    reservas_pasadas = Reserva.objects.filter(
        fecha__gte=inicio_pasada,
        fecha__lt=inicio,
        estado="Activa"
    ).count()

    # ==============================
    #  ACTIVIDADES
    # ==============================
    actividades_activas = Actividad.objects.filter(
        estado="Activa"
    ).count()

    # ==============================
    #  MÉTRICAS PARA IA / PDF
    # ==============================
    datos = {
        "Total recaudado (7 días)": total_recaudado,
        "Transacciones autorizadas": trans_sem,
        "Certificados emitidos": certificados_semana,
        "Reservas activas esta semana": reservas_semana,
        "Actividades activas": actividades_activas,
    }

    grafico_path = generar_grafico_semanal()
    grafico_base64 = cargar_imagen_base64(grafico_path)

    vecino_id = request.session["vecino_id"]
    vecino = Vecino.objects.get(id_vecino=vecino_id)
    correo_usuario = vecino.correo

    payload = {
        "evento": "reporte_ia",
        "correo_usuario": correo_usuario,

        "rango_actual": {
            "inicio": inicio.strftime("%Y-%m-%d"),
            "fin": hoy.strftime("%Y-%m-%d"),
        },
        "rango_anterior": {
            "inicio": inicio_pasada.strftime("%Y-%m-%d"),
            "fin": inicio.strftime("%Y-%m-%d"),
        },

        "datos": datos,
        "total_recaudado": total_recaudado,
        "transacciones_semana": trans_sem,
        "transacciones_semana_pasada": trans_sem_pas,
        "certificados": certificados_semana,
        "certificados_pasados": certificados_pasados,
        "reservas": reservas_semana,
        "reservas_pasadas": reservas_pasadas,
        "actividades_activas": actividades_activas,

        "grafico_base64": grafico_base64,
        "grafico_nombre": "grafico_semanal.png",

        "transacciones": [
            {
                "fecha": t.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                "monto": t.monto,
                "vecino": t.id_vecino.nombre if t.id_vecino else "Sistema",
            }
            for t in transacciones_actuales
        ],

        "resumen_prompt": (
            "Usa HTML simple para que las respuestas sean ordenadas. "
            "Genera un resumen ejecutivo profesional basado en las métricas entregadas."
        ),
        "comparativo_prompt": (
            "Usa HTML simple. Compara la semana actual con la anterior "
            "destacando aumentos o disminuciones."
        ),
        "alertas_prompt": (
            "Usa HTML simple. Genera alertas si detectas caídas, "
            "anomalías o métricas preocupantes."
        ),
        "proyeccion_prompt": (
            "Usa HTML simple. Proyecta la próxima semana según tendencias actuales."
        ),
    }

    notificar_n8n("reporte_ia", payload)

    #  Aquí cambiamos el comportamiento: solo mensaje flash + redirección al panel
    messages.success(request, "Reporte generado. Se enviará a su correo en unos minutos.")

    return redirect("panel_auditoria")


