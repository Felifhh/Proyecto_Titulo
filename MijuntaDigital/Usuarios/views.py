# ==============================================
# IMPORTACIONES
# ==============================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.hashers import check_password
from Auditoria.utils import registrar_evento  # 👈 NUEVA IMPORTACIÓN

# Formularios y Modelos
from .forms import RegistroVecinoForm, LoginForm, FotoPerfilForm
from .models import Vecino, Rol
from Certificados.models import Certificado
from Solicitudes.models import Solicitud
from Reserva.models import Reserva
from Usuarios.decorators import require_role
import requests


def notificar_n8n(evento, datos):
    webhook_url = "https://felifhhh.app.n8n.cloud/webhook/9a0798f9-34e0-4e76-b7c8-874c7f636a7a"  # URL definitiva
    try:
        requests.post(webhook_url, json={"evento": evento, **datos}, timeout=5)
        print(f" Evento '{evento}' enviado correctamente a n8n.")
    except Exception as e:
        print(f" Error enviando evento a n8n: {e}")




# ==============================================
# REGISTRO DE NUEVO VECINO
# ==============================================
@require_http_methods(["GET", "POST"])
def registro_vecino(request):
    """
    Permite que un vecino se registre en el sistema.
    El registro queda en estado "Pendiente" hasta ser aprobado por la Directiva.
    """
    if request.method == "POST":
        form = RegistroVecinoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            registrar_evento(request, "Registro de nuevo vecino", "Éxito")
            messages.success(request, "Registro enviado correctamente. Queda pendiente de validación por la directiva.")
            return redirect('usuarios_registro_ok')
        else:
            registrar_evento(request, "Intento de registro fallido", "Error en validación")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = RegistroVecinoForm()

    return render(request, "Usuarios/registro.html", {"form": form})


def registro_ok(request):
    """Página de confirmación luego del registro."""
    return render(request, "Usuarios/registro_ok.html")


# ==============================================
# VALIDACIÓN DE REGISTROS (solo directiva)
# ==============================================

@require_role(['presidente', 'secretario', 'tesorero'])
def vista_directiva(request):
    """
    Muestra la página de gestión de la directiva.
    Solo pueden acceder los roles:
    Presidente, Secretario, Tesorero y Vecino.
    Cualquier otro usuario será redirigido al home.
    """
    return render(request, "Usuarios/Directiva.html")


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


# ==============================================
# APROBACIÓN / RECHAZO DE VECINOS
# ==============================================
@require_role('presidente')
@require_POST
def aprobar_vecino(request, pk):
    vecino = get_object_or_404(Vecino, pk=pk)
    vecino.estado = "Activo"
    vecino.save()

    registrar_evento(request, f"Aprobación de vecino {vecino.nombre}", "Éxito")

    notificar_n8n("cuenta_aprobada", {
        "nombre": vecino.nombre,
        "correo": vecino.correo,
        "run": vecino.run
    })
    messages.success(request, f"{vecino.nombre} ha sido aprobado correctamente.")
    return redirect("usuarios_pendientes")


@require_role('presidente')
@require_POST
def rechazar_vecino(request, pk):
    vecino = get_object_or_404(Vecino, pk=pk)
    vecino.estado = "Rechazado"
    vecino.save()

    registrar_evento(request, f"Rechazo de vecino {vecino.nombre}", "Éxito")

    notificar_n8n("cuenta_rechazada", {
        "nombre": vecino.nombre,
        "correo": vecino.correo,
        "run": vecino.run
    })
    messages.warning(request, f"{vecino.nombre} ha sido rechazado.")
    return redirect("usuarios_pendientes")



# ==============================================
# LOGIN / LOGOUT
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

                registrar_evento(request, f"Inicio de sesión de {vecino.nombre}", "Éxito")
                messages.success(request, f"Bienvenido {vecino.nombre}")
            else:
                registrar_evento(request, f"Intento fallido de login ({run})", "Contraseña incorrecta")
                messages.error(request, "Contraseña incorrecta.")
        except Vecino.DoesNotExist:
            registrar_evento(request, f"Intento de login con RUN inexistente ({run})", "RUN no encontrado")
            messages.error(request, "RUN no encontrado o no activo.")

        return redirect("home")
    return redirect("home")


def logout_view(request):
    """
    Cierra sesión y elimina todos los datos guardados en request.session.
    """
    registrar_evento(request, "Cierre de sesión", "Éxito")
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
    reservas = Reserva.objects.filter(id_vecino=perfil).order_by("-fecha")[:5]


# ==============================================
# CAMBIO DE ROL
# ==============================================
def perfil_vecino(request, id_vecino):
    """
    Permite visualizar y modificar el perfil de un vecino.
    Incluye auditoría de cambios de rol o foto.
    """
    vecino_id = request.session.get("vecino_id")
    if not vecino_id:
        messages.error(request, "Debes iniciar sesión para acceder al perfil.")
        return redirect("home")

    usuario_sesion = get_object_or_404(Vecino, pk=vecino_id)
    perfil = get_object_or_404(Vecino, pk=id_vecino)

    if usuario_sesion.id_vecino != perfil.id_vecino and usuario_sesion.id_rol.nombre not in ["Presidente", "Secretario", "Tesorero"]:
        messages.error(request, "No tienes permisos para ver este perfil.")
        return redirect("home")

    certificados = Certificado.objects.filter(id_vecino=perfil).order_by("-fecha_emision")[:5]
    solicitudes = Solicitud.objects.filter(id_vecino=perfil).order_by("-fecha_creacion")[:5]
    reservas = Reserva.objects.filter(id_vecino=perfil).order_by("-fecha")[:5]

    # --- CAMBIO DE ROL (solo presidente) ---
    if request.method == "POST" and "rol_id" in request.POST and usuario_sesion.id_rol.nombre == "Presidente":
        nuevo_rol_id = request.POST.get("rol_id")
        nuevo_rol = Rol.objects.get(pk=nuevo_rol_id)
        perfil.id_rol = nuevo_rol
        perfil.save()
        registrar_evento(request, f"Cambio de rol de {perfil.nombre} a {nuevo_rol.nombre}", "Éxito")
        messages.success(request, f"El rol de {perfil.nombre} ha sido actualizado a {nuevo_rol.nombre}.")
        return redirect("perfil_vecino", id_vecino=perfil.id_vecino)

    # --- ACTUALIZACIÓN DE FOTO ---
    if request.method == "POST" and "foto" in request.FILES:
        form_foto = FotoPerfilForm(request.POST, request.FILES, instance=perfil)
        if form_foto.is_valid():
            form_foto.save()
            registrar_evento(request, f"Actualización de foto de perfil de {perfil.nombre}", "Éxito")
            messages.success(request, "Foto de perfil actualizada correctamente.")
            return redirect("perfil_vecino", id_vecino=perfil.id_vecino)
    else:
        form_foto = FotoPerfilForm(instance=perfil)

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


# ==============================================
# ACTIVAR / DESACTIVAR USUARIOS
# ==============================================
@require_role('presidente')
def desactivar_vecino(request, id_vecino):
    vecino = get_object_or_404(Vecino, pk=id_vecino)
    vecino.estado = "Desactivado"
    vecino.save()

    registrar_evento(request, f"Desactivación de vecino {vecino.nombre}", "Éxito")
    messages.info(request, f"{vecino.nombre} ha sido desactivado.")
    return redirect("gestion_usuarios")


@require_role('presidente')
def activar_vecino(request, id_vecino):
    vecino = get_object_or_404(Vecino, pk=id_vecino)
    vecino.estado = "Activo"
    vecino.save()

    registrar_evento(request, f"Reactivación de vecino {vecino.nombre}", "Éxito")
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
