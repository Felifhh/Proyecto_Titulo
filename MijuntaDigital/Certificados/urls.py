from django.urls import path
from . import views

urlpatterns = [
    path('descargar/<str:folio>/', views.descargar_certificado_pdf, name='certificado_pdf'),

        # --- Vistas del vecino ---
    path('solicitar/', views.solicitar_certificado, name='solicitar_certificado'),
    path('mis/', views.mis_certificados, name='mis_certificados'),

    # --- Vistas del directorio ---
    path('revisar/', views.revisar_certificados, name='revisar_certificados'),
    path('aprobar/<int:id_certificado>/', views.aprobar_certificado, name='aprobar_certificado'),
    path('rechazar/<int:id_certificado>/', views.rechazar_certificado, name='rechazar_certificado'),
]


