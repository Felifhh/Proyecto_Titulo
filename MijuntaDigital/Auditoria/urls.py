from django.urls import path
from . import views

urlpatterns = [
    path("panel/", views.panel_auditoria, name="panel_auditoria"),
    path("reportes/pdf/", views.descargar_reporte_pdf, name="descargar_reporte_pdf"),

]
