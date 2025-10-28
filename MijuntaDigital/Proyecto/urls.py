from django.urls import path
from . import views

urlpatterns = [
    path('inicio/', views.proyectos_inicio, name='proyectos_inicio'),
    path('mis/', views.mis_proyectos, name='mis_proyectos'),
    path('crear/', views.crear_proyecto, name='crear_proyecto'),
    path('gestionar/', views.gestionar_proyectos, name='gestionar_proyectos'),
    path('detalle/<int:id_proyecto>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('detalle-directiva/<int:id_proyecto>/', views.detalle_proyecto_directiva, name='detalle_proyecto_directiva'),
    path('votacion/', views.proyectos_votacion, name='proyectos_votacion'),
    path('votar/<int:id_proyecto>/<str:decision>/', views.votar_proyecto, name='votar_proyecto'),
    path('actualizar/<int:id_proyecto>/<str:accion>/', views.actualizar_estado_proyecto, name='actualizar_estado_proyecto'),
]
