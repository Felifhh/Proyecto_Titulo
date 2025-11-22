from django.apps import AppConfig

class MijuntaDigitalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MijuntaDigital'

    def ready(self):
        # Importar aquí para evitar errores antes de tiempo
        from .scheduler import start_scheduler

        # Evitar que el scheduler se inicie dos veces (Django lo hace en runserver)
        if 'runserver' in __import__('sys').argv:
            start_scheduler()
