import datetime
from django.db.models import Sum, Count
from django.conf import settings
import os

from pagos.models import Transaccion # ajusta tu modelo
from Reserva.models import Reserva    # ajusta tu modelo
from Certificados.models import Certificado  # ajusta tu modelo


def obtener_metricas():
    """
    Obtiene métricas reales desde la BD para el reporte semanal.
    """
    hoy = datetime.date.today()
    inicio_semana = hoy - datetime.timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    # ===========================
    # INGRESOS
    # ===========================
    total_semana = Transaccion.objects.filter(
        fecha__date__gte=inicio_semana
    ).aggregate(total=Sum("monto"))["total"] or 0

    total_mes = Transaccion.objects.filter(
        fecha__date__gte=inicio_mes
    ).aggregate(total=Sum("monto"))["total"] or 0

    semana_pasada = Transaccion.objects.filter(
        fecha__date__lt=inicio_semana,
        fecha__date__gte=inicio_semana - datetime.timedelta(days=7)
    ).aggregate(total=Sum("monto"))["total"] or 0

    # Variación semanal %
    if semana_pasada == 0:
        variacion = 100 if total_semana > 0 else 0
    else:
        variacion = round(((total_semana - semana_pasada) / semana_pasada) * 100, 1)

    # ===========================
    # RESERVAS
    # ===========================
    reservas_semana = Reserva.objects.filter(
        fecha__gte=inicio_semana
    ).count()

    # ===========================
    # CERTIFICADOS
    # ===========================
    certificados_semana = Certificado.objects.filter(
        fecha_emision__gte=inicio_semana
    ).count()

    # ===========================
    # ALERTAS IA (básicas por ahora)
    # ===========================
    alertas = []
    if total_semana < semana_pasada * 0.7:
        alertas.append("⚠ Caída fuerte en la recaudación semanal (-30% o más).")

    if reservas_semana < 3:
        alertas.append("⚠ Baja actividad en las reservas de espacios.")

    if certificados_semana == 0:
        alertas.append("⚠ No se emitieron certificados esta semana.")

    # ===========================
    # TENDENCIAS IA
    # ===========================
    tendencia_general = (
        "Crecimiento"
        if variacion > 0 else
        "Caída"
        if variacion < 0 else
        "Estable"
    )

    tendencias = [
        f"La variación semanal de ingresos fue de {variacion}%.",
        f"Actividad de reservas: {reservas_semana} en la semana.",
        f"Certificados emitidos: {certificados_semana}.",
        f"Tendencia general: {tendencia_general}.",
    ]

    # ===========================
    # SALIDA FINAL
    # ===========================
    return {
        "total_recaudado_semana": total_semana,
        "total_recaudado_mes": total_mes,
        "variacion_semanal": variacion,
        "reservas_semana": reservas_semana,
        "certificados_semana": certificados_semana,
        "tendencia_general": tendencia_general,
        "alertas": alertas,
        "tendencias": tendencias,
    }
