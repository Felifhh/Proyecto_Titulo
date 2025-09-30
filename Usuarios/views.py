from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from .forms import RegistroVecinoForm
from .models import Vecino
from .forms import LoginForm
from django.contrib.auth.hashers import check_password


@require_http_methods(["GET", "POST"])
def registro_vecino(request):
    if request.method == "POST":
        form = RegistroVecinoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro enviado. Queda pendiente de validación.")
            return redirect('usuarios_registro_ok')
    else:
        form = RegistroVecinoForm()
    return render(request, "Usuarios/registro.html", {"form": form})

def registro_ok(request):
    return render(request, "Usuarios/registro_ok.html")

# Validación (vista para directorio)
def lista_pendientes(request):
    pendientes = Vecino.objects.filter(estado="Pendiente")
    return render(request, "Usuarios/pendientes.html", {"items": pendientes})

@require_POST
def aprobar_vecino(request, pk):
    vecino = get_object_or_404(Vecino, pk=pk)
    vecino.estado = "Activo"
    vecino.save()
    messages.success(request, f"{vecino.nombre} aprobado.")
    return redirect("usuarios_pendientes")

@require_POST
def rechazar_vecino(request, pk):
    vecino = get_object_or_404(Vecino, pk=pk)
    vecino.estado = "Rechazado"
    vecino.save()
    messages.warning(request, f"{vecino.nombre} rechazado.")
    return redirect("usuarios_pendientes")


def login_view(request):
    if request.method == "POST":
        run = request.POST.get("run")
        contrasena = request.POST.get("contrasena")

        try:
            vecino = Vecino.objects.get(run=run, estado="Activo")
            if check_password(contrasena, vecino.contrasena):
                request.session["vecino_id"] = vecino.id_vecino
                request.session["vecino_nombre"] = vecino.nombre
                messages.success(request, f"Bienvenido {vecino.nombre}")
            else:
                messages.error(request, "Contraseña incorrecta")
        except Vecino.DoesNotExist:
            messages.error(request, "RUN no encontrado o no activo")

        return redirect("home")  # Siempre redirige al home
    return redirect("home")


def logout_view(request):
    request.session.flush()  # limpia toda la sesión
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("home")