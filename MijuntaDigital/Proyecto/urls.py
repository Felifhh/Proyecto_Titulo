from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_postulacion, name='proyectos_crear'),
    path('lista/', views.lista_postulaciones, name='proyectos_lista'),
    path('todos/', views.lista_todos_proyectos, name='proyectos_todos'),

]
