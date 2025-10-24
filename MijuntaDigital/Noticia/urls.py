# Noticias/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_noticias, name='lista_noticias'),
    path('crear/', views.crear_noticia, name='crear_noticia'),
    path('<int:id_noticia>/', views.detalle_noticia, name='detalle_noticia'),
]
