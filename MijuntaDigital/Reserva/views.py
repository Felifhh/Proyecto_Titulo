from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Usuarios.decorators import require_role
from .models import EspacioComunal
from .forms import EspacioForm

@require_role(['presidente', 'secretario', 'tesorero'])
def gestionar_espacios(request):
    """
    Panel de gestión de espacios comunales.
    Incluye buscador por nombre y subida de imágenes.
    """
    query = request.GET.get('buscar', '').strip()

    espacios_activos = EspacioComunal.objects.filter(estado="Activo")
    espacios_inactivos = EspacioComunal.objects.filter(estado="Inactivo")

    if query:
        espacios_activos = espacios_activos.filter(nombre__icontains=query)
        espacios_inactivos = espacios_inactivos.filter(nombre__icontains=query)

    return render(request, "Reserva/gestion_espacios.html", {
        "activos": espacios_activos.order_by("-fecha_creacion"),
        "inactivos": espacios_inactivos.order_by("-fecha_creacion"),
        "query": query,
    })


@require_role(['presidente', 'secretario', 'tesorero'])
def crear_espacio(request):
    """Crea un nuevo espacio comunal con imagen obligatoria."""
    if request.method == "POST":
        form = EspacioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Espacio comunal creado correctamente.")
            return redirect('gestionar_espacios')
        else:
            messages.error(request, "Revisa los datos ingresados. Todos los campos son obligatorios.")
    else:
        form = EspacioForm()

    return render(request, "Reserva/crear_espacio.html", {"form": form, "modo": "crear"})


@require_role(['presidente', 'secretario', 'tesorero'])
def cambiar_estado_espacio(request, id_espacio):
    """Activa o inactiva un espacio comunal."""
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)
    espacio.estado = "Activo" if espacio.estado == "Inactivo" else "Inactivo"
    espacio.save()
    messages.info(request, f"El estado de {espacio.nombre} ha sido cambiado a {espacio.estado}.")
    return redirect("gestionar_espacios")


@require_role(['presidente', 'secretario', 'tesorero'])
def eliminar_espacio(request, id_espacio):
    """Elimina un espacio definitivamente."""
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)
    espacio.delete()
    messages.error(request, f"{espacio.nombre} ha sido eliminado permanentemente.")
    return redirect("gestionar_espacios")

@require_role(['presidente', 'secretario', 'tesorero'])
def desactivar_espacio(request, id_espacio):
    """Desactiva un espacio comunal (solo directiva)."""
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)
    espacio.estado = 'Inactivo'
    espacio.save()
    messages.warning(request, f"El espacio '{espacio.nombre}' ha sido desactivado.")
    return redirect('gestionar_espacios')


@require_role(['presidente', 'secretario', 'tesorero'])
def activar_espacio(request, id_espacio):
    """Activa un espacio comunal (solo directiva)."""
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)
    espacio.estado = 'Activo'
    espacio.save()
    messages.success(request, f"El espacio '{espacio.nombre}' ha sido activado correctamente.")
    return redirect('gestionar_espacios')

@require_role(['presidente', 'secretario', 'tesorero'])
def editar_espacio(request, id_espacio):
    """
    Permite modificar un espacio comunal existente.
    No se puede cambiar el estado desde aquí.
    """
    espacio = get_object_or_404(EspacioComunal, pk=id_espacio)

    if request.method == 'POST':
        form = EspacioForm(request.POST, request.FILES, instance=espacio)
        if form.is_valid():
            form.save()
            messages.success(request, f"El espacio '{espacio.nombre}' fue actualizado correctamente.")
            return redirect('gestionar_espacios')
        else:
            messages.error(request, "Verifica los datos ingresados. Hay errores en el formulario.")
    else:
        form = EspacioForm(instance=espacio)

    return render(request, 'Reserva/editar_espacio.html', {
        'form': form,
        'modo': 'editar',
        'espacio': espacio
    })