from django.urls import path
from . import views

urlpatterns = [
    path('solicitar/', views.solicitar_certificado, name='certificado_solicitar'),
    path('descargar/<str:folio>/', views.descargar_certificado_pdf, name='certificado_pdf'),
]

