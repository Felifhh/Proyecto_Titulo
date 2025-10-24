from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from .models import Noticia
from Notificaciones.models import Notificacion

def crear_noticia(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        link = request.POST.get('link')
        imagen = request.FILES.get('imagen')
        vecino_id = request.session.get('vecino_id')

        if not vecino_id:
            messages.error(request, "Debes iniciar sesión para publicar una noticia.")
            return redirect('login')

        noticia = Noticia.objects.create(
            id_vecino_id=vecino_id,
            titulo=titulo,
            contenido=contenido,
            link=link,
            imagen=imagen
        )

        # Crear notificación global
        Notificacion.objects.create(
            titulo="Nueva noticia publicada",
            mensaje=f"Se ha publicado una nueva noticia: {noticia.titulo}",
            tipo='global'
        )

        messages.success(request, "Noticia publicada correctamente.")
        return redirect('lista_noticias')

    return render(request, 'Noticias/crear_noticia.html')


def lista_noticias(request):
    q = request.GET.get('q', '')
    noticias = Noticia.objects.all().order_by('-fecha_publicacion')
    if q:
        noticias = noticias.filter(titulo__icontains=q)
    return render(request, 'Noticias/lista_noticias.html', {'noticias': noticias, 'q': q})


def detalle_noticia(request, id_noticia):
    """
    Muestra el detalle completo de una noticia publicada.
    """
    noticia = get_object_or_404(Noticia, id_noticia=id_noticia)
    return render(request, 'Noticias/detalle_noticia.html', {'noticia': noticia})
