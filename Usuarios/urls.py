from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_vecino, name='usuarios_registro'),
    path('registro/ok/', views.registro_ok, name='usuarios_registro_ok'),

    path('validacion/pendientes/', views.lista_pendientes, name='usuarios_pendientes'),
    path('validacion/<int:pk>/aprobar/', views.aprobar_vecino, name='usuarios_aprobar'),
    path('validacion/<int:pk>/rechazar/', views.rechazar_vecino, name='usuarios_rechazar'),

    path('login/', views.login_view, name='usuarios_login'),
    path('logout/', views.logout_view, name='usuarios_logout'),
]
