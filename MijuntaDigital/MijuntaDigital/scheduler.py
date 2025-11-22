from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django.utils import timezone

def ejecutar_cierre_automatico():
    call_command("cerrar_votaciones")

def start_scheduler():
    scheduler = BackgroundScheduler()

    # Cada 10 segundos (para pruebas)
    scheduler.add_job(
        ejecutar_cierre_automatico,
        'interval',
        seconds=30,
        id='cierre_votaciones_job',
        replace_existing=True
    )

    scheduler.start()
    print("✔ Scheduler iniciado correctamente")


