from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from Actividades.views import home


urlpatterns = [
    path("admin/", admin.site.urls),
    # Página principal (puedes luego cambiar TemplateView por una vista real)
    path("", home, name="home"),
    # Rutas de tus apps
    path("usuarios/", include("Usuarios.urls")),
    path("certificados/", include("Certificados.urls")),
    path("proyectos/", include("Proyecto.urls")),
    path("reservas/", include("Reserva.urls")),
    path("actividades/", include("Actividades.urls")),
    path("pagos/", include("pagos.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
