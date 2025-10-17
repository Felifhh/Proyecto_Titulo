from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProyectoForm
from .models import Proyecto
from Usuarios.decorators import require_role
from django.db.models import Case, When, Value, IntegerField
from django.conf import settings
import os

# -----------------------------
# CREACIÓN DE PROYECTOS
# -----------------------------
@require_role(['vecino', 'presidente', 'secretario', 'tesorero'])
def crear_postulacion(request):
    vecino = request.vecino

    # 🧮 Contar proyectos activos (en revisión o aprobados)
    proyectos_activos = Proyecto.objects.filter(
        id_vecino=vecino,
        estado__in=['En revisión', 'Aprobado']
    ).count()

    if proyectos_activos >= 2:
        messages.error(
            request,
            "Ya tienes 2 proyectos activos (en revisión o aprobados). "
            "Espera a que se rechace alguno para crear uno nuevo."
        )
        return redirect('proyectos_lista')

    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES)
        if form.is_valid():
            imagen = form.cleaned_data.get('documento_adj')

            # ⚠️ Validar que se haya subido una imagen
            if not imagen or isinstance(imagen, str):
                messages.error(request, "Debe adjuntar una imagen válida antes de enviar.")
                return redirect('proyectos_crear')

            # 📁 Crear directorio destino si no existe
            ruta_dir = os.path.join(settings.MEDIA_ROOT, 'Proyecto')
            os.makedirs(ruta_dir, exist_ok=True)

            # 🧾 Determinar nombre de archivo basado en el RUT del vecino
            rut = getattr(vecino, 'rut', f'vecino_{vecino.id_vecino}')
            total = Proyecto.objects.filter(id_vecino=vecino).count() + 1

            # 🧩 Obtener extensión de archivo de forma segura
            nombre_original = getattr(imagen, 'name', '')
            extension = os.path.splitext(nombre_original)[1].lower()

            # 🚫 Validar tipo de archivo
            if extension not in ['.jpg', '.jpeg', '.png']:
                messages.error(request, "Solo se permiten imágenes en formato JPG o PNG.")
                return redirect('proyectos_crear')

            # 🏷️ Nombre final del archivo
            nombre_archivo = f"{rut}_proyecto{total}{extension}"
            ruta_completa = os.path.join(ruta_dir, nombre_archivo)

            # 💾 Guardar físicamente el archivo
            try:
                with open(ruta_completa, 'wb+') as destino:
                    for chunk in imagen.chunks():
                        destino.write(chunk)
            except Exception as e:
                messages.error(request, f"Error al guardar la imagen: {e}")
                return redirect('proyectos_crear')

            # 🧱 Crear registro del proyecto en la base de datos
            Proyecto.objects.create(
                id_vecino=vecino,
                titulo=form.cleaned_data['titulo'],
                descripcion=form.cleaned_data['descripcion'],
                presupuesto=form.cleaned_data['presupuesto'],
                documento_adj=f"Proyecto/{nombre_archivo}",
                estado="En revisión",
                fecha_postulacion=None
            )

            messages.success(request, " Postulación creada correctamente con imagen de referencia.")
            return redirect('proyectos_lista')

        else:
            messages.error(request, "Error en el formulario. Revise los campos e intente nuevamente.")
    else:
        form = ProyectoForm()

    return render(request, 'Proyectos/crear_postulacion.html', {'form': form})


# -----------------------------
# LISTAR POSTULACIONES PROPIAS
# -----------------------------
@require_role(['vecino', 'presidente', 'secretario', 'tesorero'])
def lista_postulaciones(request):
    """Muestra los proyectos del vecino actual con orden de prioridad."""
    vecino = request.vecino

    proyectos = Proyecto.objects.filter(id_vecino=vecino).annotate(
        prioridad=Case(
            When(estado='En revisión', then=Value(1)),
            When(estado='Aprobado', then=Value(2)),
            When(estado='Rechazado', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('prioridad', '-fecha_postulacion')

    return render(request, 'Proyectos/lista_postulaciones.html', {'proyectos': proyectos})


# -----------------------------
# LISTAR TODAS LAS POSTULACIONES (solo aprobadas)
# -----------------------------
@require_role(['presidente', 'secretario', 'tesorero', 'vecino'])
def lista_todos_proyectos(request):
    """Muestra solo los proyectos aprobados (aceptados) por el directorio."""
    proyectos = Proyecto.objects.select_related('id_vecino').filter(
        estado='Aprobado'
    ).order_by('-fecha_postulacion')

    return render(request, 'Proyectos/lista_todos.html', {'proyectos': proyectos})
