from django.urls import path
from . import views

urlpatterns = [
    # --- Acciones del vecino ---
    path('crear/', views.crear_solicitud, name='crear_solicitud'),
    path('mis/', views.mis_solicitudes, name='mis_solicitudes'),

    # --- Acciones de la directiva ---
    path('gestionar/', views.gestionar_solicitudes, name='gestionar_solicitudes'),
    path('<int:id_solicitud>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('<int:id_solicitud>/actualizar/', views.actualizar_estado_solicitud, name='actualizar_estado_solicitud'),
]
