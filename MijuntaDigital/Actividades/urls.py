from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_actividades, name='lista_actividades'),
    path('<int:id_actividad>/', views.detalle_actividad, name='detalle_actividad'),
    path('crear/', views.crear_actividad, name='crear_actividad'),
    path('cancelar/<int:id_actividad>/', views.cancelar_actividad, name='cancelar_actividad'),
    path('finalizar/<int:id_actividad>/', views.finalizar_actividad, name='finalizar_actividad'),
    path('inscribirse/<int:id_actividad>/', views.inscribirse_actividad, name='inscribirse_actividad'),
    path('cancelar_inscripcion/<int:id_actividad>/', views.cancelar_inscripcion, name='cancelar_inscripcion'),  # ✅ este
]
