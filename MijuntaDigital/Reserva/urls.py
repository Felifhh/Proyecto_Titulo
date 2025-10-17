from django.urls import path
from . import views

urlpatterns = [
    path('espacios/', views.gestionar_espacios, name='gestionar_espacios'),
    path('espacios/crear/', views.crear_espacio, name='crear_espacio'),
    path('espacios/<int:id_espacio>/cambiar_estado/', views.cambiar_estado_espacio, name='cambiar_estado_espacio'),
    path('espacios/<int:id_espacio>/eliminar/', views.eliminar_espacio, name='eliminar_espacio'),
    path('espacios/<int:id_espacio>/editar/', views.editar_espacio, name='editar_espacio'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('catalogo-espacios/', views.ver_espacios_comunales, name='ver_espacios_comunales'),
    path('espacios/reservar/<int:id_espacio>/', views.reservar_desde_catalogo, name='reservar_desde_catalogo'),
    path('disponibilidad/<int:id_espacio>/', views.ver_disponibilidad, name='ver_disponibilidad'),


    path('espacios/<int:id_espacio>/desactivar/', views.desactivar_espacio, name='desactivar_espacio'),
    path('espacios/<int:id_espacio>/activar/', views.activar_espacio, name='activar_espacio'),
]

