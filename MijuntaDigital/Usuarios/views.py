# ==============================================
# IMPORTACIONES
# ==============================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.hashers import check_password

# Formularios y Modelos
from .forms import RegistroVecinoForm, LoginForm, FotoPerfilForm
from .models import Vecino, Rol
from Certificados.models import Certificado
from Solicitudes.models import Solicitud
from Reserva.models import Reserva

# Decorador personalizado (rol)
from Usuarios.decorators import require_role





# ==============================================
# REGISTRO DE NUEVO VECINO
# ==============================================

@require_http_methods(["GET", "POST"])
def registro_vecino(request):
    """
    Permite que un vecino se registre en el sistema.
    El registro queda en estado "Pendiente" hasta ser aprobado por el Presidente.
    Ahora permite adjuntar una foto de perfil y un archivo de evidencia.
    """
    if request.method == "POST":
        form = RegistroVecinoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                " Registro enviado correctamente. Queda pendiente de validación por la directiva."
            )
            return redirect('usuarios_registro_ok')
        else:
            messages.error(request, " Verifica los datos ingresados. Hay errores en el formulario.")
    else:
        form = RegistroVecinoForm()

    return render(request, "Usuarios/registro.html", {"form": form})


# AGREGA ESTA FUNCIÓN (probablemente la borraste sin querer)
def registro_ok(request):
    """Página de confirmación luego del registro."""
    return render(request, "Usuarios/registro_ok.html")


# ==============================================
# VALIDACIÓN DE REGISTROS (solo directiva)
# ==============================================


def lista_pendientes(request):
    """
    Muestra la lista de vecinos en estado 'Pendiente'
    (visible solo para la directiva).
    """
    # Solo Presidente / Secretario / Tesorero pueden ver esto
    rol = request.session.get("vecino_rol", "").lower()
    if rol not in ["presidente", "secretario", "tesorero"]:
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect("home")

    pendientes = Vecino.objects.filter(estado="Pendiente")
    return render(request, "Usuarios/pendientes.html", {"items": pendientes})


def detalle_vecino(request, pk):
    """
    Muestra toda la información del registro de un vecino pendiente.
    Incluye evidencia y foto.
    """
    rol = request.session.get("vecino_rol", "").lower()
    if rol not in ["presidente", "secretario", "tesorero"]:
        messages.error(request, "No tienes permisos para ver esta solicitud.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=pk)
    return render(request, "Usuarios/detalle_vecino.html", {"vecino": vecino})


# --- ACCIONES: APROBAR / RECHAZAR ---
@require_role('presidente')
@require_POST
def aprobar_vecino(request, pk):
    """
    Cambia el estado de un vecino pendiente a 'Activo'.
    Solo el Presidente puede aprobar.
    """
    vecino = get_object_or_404(Vecino, pk=pk)
    vecino.estado = "Activo"
    vecino.save()
    messages.success(request, f" {vecino.nombre} ha sido aprobado correctamente.")
    return redirect("usuarios_pendientes")


@require_role('presidente')
@require_POST
def rechazar_vecino(request, pk):
    """
    Cambia el estado de un vecino pendiente a 'Rechazado'.
    Solo el Presidente puede realizar esta acción.
    """
    vecino = get_object_or_404(Vecino, pk=pk)
    vecino.estado = "Rechazado"
    vecino.save()
    messages.warning(request, f" {vecino.nombre} ha sido rechazado.")
    return redirect("usuarios_pendientes")


# ==============================================
# AUTENTICACIÓN (LOGIN / LOGOUT)
# ==============================================

def login_view(request):
    """
    Inicia sesión verificando RUN y contraseña del vecino activo.
    Almacena datos de sesión: id, nombre y rol.
    """
    if request.method == "POST":
        run = request.POST.get("run")
        contrasena = request.POST.get("contrasena")

        try:
            vecino = Vecino.objects.get(run=run, estado="Activo")
            if check_password(contrasena, vecino.contrasena):
                # Guardar datos de sesión
                request.session["vecino_id"] = vecino.id_vecino
                request.session["vecino_nombre"] = vecino.nombre
                request.session["vecino_rol"] = (vecino.id_rol.nombre or '').strip().lower()

                messages.success(request, f"Bienvenido {vecino.nombre}")
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Vecino.DoesNotExist:
            messages.error(request, "RUN no encontrado o no activo.")

        return redirect("home")
    return redirect("home")


def logout_view(request):
    """
    Cierra sesión y elimina todos los datos guardados en request.session.
    """
    request.session.flush()
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("home")


# ==============================================
# PERFIL DE VECINO
# ==============================================

def perfil_vecino(request, id_vecino):
    """
    Muestra el perfil de un vecino.
    Solo el propio usuario o un miembro de la directiva (Presidente, Secretario, Tesorero)
    puede ver otros perfiles.
    También permite al Presidente cambiar roles o subir una nueva foto.
    """
    # Verificar sesión activa
    vecino_id = request.session.get("vecino_id")
    if not vecino_id:
        messages.error(request, "Debes iniciar sesión para acceder al perfil.")
        return redirect("home")

    usuario_sesion = get_object_or_404(Vecino, pk=vecino_id)
    perfil = get_object_or_404(Vecino, pk=id_vecino)

    # Control de permisos de acceso
    if usuario_sesion.id_vecino != perfil.id_vecino and usuario_sesion.id_rol.nombre not in ["Presidente", "Secretario", "Tesorero"]:
        messages.error(request, "No tienes permisos para ver este perfil.")
        return redirect("home")

    # Datos de actividad reciente
    certificados = Certificado.objects.filter(id_vecino=perfil).order_by("-fecha_emision")[:5]
    solicitudes = Solicitud.objects.filter(id_vecino=perfil).order_by("-fecha_creacion")[:5]
    reservas = Reserva.objects.filter(id_vecino=perfil).order_by("-fecha_reserva")[:5]

    # -----------------------------
    # CAMBIO DE ROL (solo Presidente)
    # -----------------------------
    if request.method == "POST" and "rol_id" in request.POST and usuario_sesion.id_rol.nombre == "Presidente":
        nuevo_rol_id = request.POST.get("rol_id")
        nuevo_rol = Rol.objects.get(pk=nuevo_rol_id)

        # Si el nuevo rol es Presidente → transferir el cargo
        if nuevo_rol.nombre == "Presidente":
            anterior_presidente = Vecino.objects.filter(id_rol__nombre="Presidente").first()
            if anterior_presidente:
                anterior_presidente.id_rol = Rol.objects.get(nombre="Vecino")
                anterior_presidente.save()

            usuario_sesion.id_rol = Rol.objects.get(nombre="Vecino")
            usuario_sesion.save()
            perfil.id_rol = nuevo_rol
            perfil.save()

            messages.success(request, f"Has delegado la presidencia a {perfil.nombre}.")
            return redirect("usuarios_logout")

        # Para cualquier otro cambio
        perfil.id_rol = nuevo_rol
        perfil.save()
        messages.success(request, f"El rol de {perfil.nombre} ha sido actualizado a {nuevo_rol.nombre}.")
        return redirect("perfil_vecino", id_vecino=perfil.id_vecino)

    # -----------------------------
    # ACTUALIZACIÓN DE FOTO
    # -----------------------------
    if request.method == "POST" and "foto" in request.FILES:
        form_foto = FotoPerfilForm(request.POST, request.FILES, instance=perfil)
        if form_foto.is_valid():
            form_foto.save()
            messages.success(request, "Foto de perfil actualizada correctamente.")
            return redirect("perfil_vecino", id_vecino=perfil.id_vecino)
    else:
        form_foto = FotoPerfilForm(instance=perfil)

    # Render del perfil
    roles = Rol.objects.all()
    return render(request, "Usuarios/perfil_vecino.html", {
        "perfil": perfil,
        "usuario_sesion": usuario_sesion,
        "roles": roles,
        "certificados": certificados,
        "solicitudes": solicitudes,
        "reservas": reservas,
        "form_foto": form_foto,
    })


# ==============================================
# GESTIÓN DE USUARIOS (solo PRESIDENTE)
# ==============================================
from django.db.models import Q

@require_role('presidente')
def gestion_usuarios(request):
    """
    Panel administrativo del Presidente.
    Muestra usuarios activos, desactivados y rechazados con pestañas y buscador.
    """
    usuario_sesion = request.vecino
    query = request.GET.get('buscar', '').strip()

    # Filtrar por estado
    vecinos_activos = Vecino.objects.filter(estado="Activo")
    vecinos_desactivados = Vecino.objects.filter(estado="Desactivado")
    vecinos_rechazados = Vecino.objects.filter(estado="Rechazado")

    # Excluir Pendientes
    vecinos_activos = vecinos_activos.exclude(estado="Pendiente")
    vecinos_desactivados = vecinos_desactivados.exclude(estado="Pendiente")
    vecinos_rechazados = vecinos_rechazados.exclude(estado="Pendiente")

    # Buscar por RUN si hay query
    if query:
        vecinos_activos = vecinos_activos.filter(run__icontains=query)
        vecinos_desactivados = vecinos_desactivados.filter(run__icontains=query)
        vecinos_rechazados = vecinos_rechazados.filter(run__icontains=query)

    # Ordenar
    vecinos_activos = vecinos_activos.order_by("-fecha_registro")
    vecinos_desactivados = vecinos_desactivados.order_by("-fecha_registro")
    vecinos_rechazados = vecinos_rechazados.order_by("-fecha_registro")

    roles = Rol.objects.all()

    return render(request, "Usuarios/gestion_usuarios.html", {
        "usuario_sesion": usuario_sesion,
        "roles": roles,
        "activos": vecinos_activos,
        "desactivados": vecinos_desactivados,
        "rechazados": vecinos_rechazados,
        "query": query,
    })


@require_role('presidente')
def desactivar_vecino(request, id_vecino):
    """Desactiva a un vecino (solo visible desde la gestión de usuarios)."""
    vecino = get_object_or_404(Vecino, pk=id_vecino)
    vecino.estado = "Desactivado"
    vecino.save()
    messages.info(request, f"{vecino.nombre} ha sido desactivado.")
    return redirect("gestion_usuarios")


@require_role('presidente')
def activar_vecino(request, id_vecino):
    """Activa un vecino previamente desactivado."""
    vecino = get_object_or_404(Vecino, pk=id_vecino)
    vecino.estado = "Activo"
    vecino.save()
    messages.success(request, f"{vecino.nombre} ha sido activado nuevamente.")
    return redirect("gestion_usuarios")


@require_role('presidente')
def cambiar_rol(request, id_vecino):
    """Actualiza el rol de un vecino (solo Presidente)."""
    if request.method == "POST":
        nuevo_rol_id = request.POST.get("rol_id")
        vecino = get_object_or_404(Vecino, pk=id_vecino)
        vecino.id_rol_id = nuevo_rol_id
        vecino.save()
        messages.success(request, f"Rol de {vecino.nombre} actualizado correctamente.")
    return redirect("gestion_usuarios")
