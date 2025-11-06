from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_documentos, name='lista_documentos'),
    path('subir/', views.subir_documento, name='subir_documento'),
    path('detalle/<int:id_documento>/', views.detalle_documento, name='detalle_documento'),
]
