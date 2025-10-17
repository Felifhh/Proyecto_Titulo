from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_actividades, name='lista_actividades'),
    path('crear/', views.crear_actividad, name='crear_actividad'),
    path('<int:id_actividad>/cancelar/', views.cancelar_actividad, name='cancelar_actividad'),
    path('<int:id_actividad>/', views.detalle_actividad, name='detalle_actividad'),
    path('<int:id_actividad>/inscribirse/', views.inscribirse_actividad, name='inscribirse_actividad'),
    path('<int:id_actividad>/cancelar/', views.cancelar_inscripcion, name='cancelar_inscripcion'),
    path('<int:id_actividad>/finalizar/', views.finalizar_actividad, name='finalizar_actividad'),
]
