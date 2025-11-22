from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.chatbot_api, name='chatbot_api'),
    path('reservar/tentativa/', views.crear_reserva_tentativa, name='crear_reserva_tentativa'),
    path('reservar/confirmar/', views.confirmar_reserva, name='confirmar_reserva'),
    path('abrir-pago/', views.abrir_pago, name='chatbot_abrir_pago'),
]
