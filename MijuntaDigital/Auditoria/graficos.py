# Auditoria/graficos.py

import os
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from django.db.models import Sum
from pagos.models import Transaccion


def generar_grafico_semanal():
    """
    Genera un gráfico semanal limpio en formato dd-mm.
    """

    hoy = timezone.now()
    inicio = hoy - timedelta(days=7)

    pagos = (
        Transaccion.objects.filter(
            fecha__gte=inicio,
            estado="Authorized"
        ).order_by("fecha")
    )

    if not pagos.exists():
        return None

    # Agrupación manual
    dias = {}

    for t in pagos:
        dia = t.fecha.date()  # ← fecha real (datetime.date)
        dias[dia] = dias.get(dia, 0) + t.monto

    fechas = list(dias.keys())
    montos = list(dias.values())

    # Ordenar por fecha
    fechas.sort()

    # --- GRAFICO ---
    plt.figure(figsize=(9, 3))

    plt.plot(fechas, montos, marker="o", linewidth=2)

    # Formato de fecha en eje X
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    plt.xticks(rotation=45)
    plt.title("Recaudación últimos 7 días")
    plt.xlabel("Fecha")
    plt.ylabel("Monto ($)")
    plt.grid(True, linestyle="--", alpha=0.5)

    ruta = os.path.join(settings.MEDIA_ROOT, "graficos/grafico_semanal.png")
    plt.tight_layout()
    plt.savefig(ruta)
    plt.close()

    return ruta
