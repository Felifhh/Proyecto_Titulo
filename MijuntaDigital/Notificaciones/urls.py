from django.urls import path
from . import views

urlpatterns = [
    path('marcar-leida/<int:notificacion_id>/', views.marcar_leida, name='marcar_leida'),
]
