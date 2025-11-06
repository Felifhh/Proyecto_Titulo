from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from Usuarios.decorators import require_role
from .models import Noticia
from Notificaciones.models import Notificacion
from Auditoria.utils import registrar_evento

# ==============================================
# CREAR NOTICIA (solo directiva)
# ==============================================
@require_role(['presidente', 'secretario', 'tesorero'])
def crear_noticia(request):
    """
    Permite al Presidente, Secretario o Tesorero crear una nueva noticia.
    Se registra en auditoría y se envía notificación global a los vecinos.
    """
    vecino_id = request.session.get("vecino_id")
    rol = request.session.get("vecino_rol", "").lower()

    if rol not in ["presidente", "secretario", "tesorero"]:
        messages.error(request, "No tienes permisos para publicar noticias.")
        return redirect("home")

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        link = request.POST.get('link')
        imagen = request.FILES.get('imagen')

        if not titulo or not contenido:
            messages.error(request, "Debes completar todos los campos obligatorios.")
            registrar_evento(request, "Intento fallido de creación de noticia (campos incompletos)", "Error")
            return redirect('crear_noticia')

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

        registrar_evento(request, f"Publicación de noticia '{noticia.titulo}'", "Éxito")
        messages.success(request, "Noticia publicada correctamente.")
        return redirect('lista_noticias')

    return render(request, 'Noticias/crear_noticia.html')



# ==============================================
# LISTA DE NOTICIAS
# ==============================================
def lista_noticias(request):
    """
    Muestra todas las noticias publicadas, con opción de búsqueda.
    """
    q = request.GET.get('q', '')
    noticias = Noticia.objects.all().order_by('-fecha_publicacion')
    if q:
        noticias = noticias.filter(titulo__icontains=q)
    return render(request, 'Noticias/lista_noticias.html', {'noticias': noticias, 'q': q})



# ==============================================
# DETALLE DE NOTICIA
# ==============================================
def detalle_noticia(request, id_noticia):
    """
    Muestra el detalle completo de una noticia publicada.
    """
    noticia = get_object_or_404(Noticia, id_noticia=id_noticia)
    registrar_evento(request, f"Visualización de noticia '{noticia.titulo}'", "Éxito")
    return render(request, 'Noticias/detalle_noticia.html', {'noticia': noticia})
