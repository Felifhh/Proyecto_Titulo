from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página principal (puedes luego cambiar TemplateView por una vista real)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('directiva/', TemplateView.as_view(template_name='Directiva.html'), name='Directiva'),
    # Rutas de tus apps
    path('usuarios/', include('Usuarios.urls')),
    path('certificados/', include('Certificados.urls')),
    path('proyectos/', include('Proyecto.urls')),
    path('reservas/', include('Reserva.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)