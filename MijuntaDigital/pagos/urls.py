from django.urls import path
from . import views

urlpatterns = [
    path('iniciar/', views.iniciar_pago, name='iniciar_pago'),
    path('retorno/', views.retorno_pago, name='retorno_pago'),
    path('retorno_certificado/', views.retorno_pago_certificado, name='retorno_pago_certificado'),
    path('retorno_reserva/', views.retorno_pago_reserva, name='retorno_pago_reserva'),


]
