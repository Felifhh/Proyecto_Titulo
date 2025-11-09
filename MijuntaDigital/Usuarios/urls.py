from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_vecino, name='usuarios_registro'),
    path('registro/ok/', views.registro_ok, name='usuarios_registro_ok'),

    path('validacion/pendientes/', views.lista_pendientes, name='usuarios_pendientes'),
    path('pendientes/<int:pk>/', views.detalle_vecino, name='usuarios_detalle'),
    path('validacion/<int:pk>/aprobar/', views.aprobar_vecino, name='usuarios_aprobar'),
    path('validacion/<int:pk>/rechazar/', views.rechazar_vecino, name='usuarios_rechazar'),
    path('perfil/<int:id_vecino>/', views.perfil_vecino, name='perfil_vecino'),
    path("recuperar/", views.solicitar_recuperacion, name="solicitar_recuperacion"),
    path("verificar-codigo/", views.verificar_codigo, name="verificar_codigo"),
    path("cambiar-contrasena/", views.cambiar_contrasena, name="cambiar_contrasena"),

    path('directiva/', views.vista_directiva, name='Directiva'),

    # Gestión (solo presidente)
    path("gestion/", views.gestion_usuarios, name="gestion_usuarios"),
    path('activar/<int:id_vecino>/', views.activar_vecino, name='activar_vecino'),
    path("desactivar/<int:id_vecino>/", views.desactivar_vecino, name="desactivar_vecino"),
    path("cambiar_rol/<int:id_vecino>/", views.cambiar_rol, name="cambiar_rol"),


    path('login/', views.login_view, name='usuarios_login'),
    path('logout/', views.logout_view, name='usuarios_logout'),
]
