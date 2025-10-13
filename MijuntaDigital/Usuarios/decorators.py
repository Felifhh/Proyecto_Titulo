from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Vecino

def require_role(*allowed_roles):
    """
    Decorador que exige sesión activa y un rol específico.
    Si no hay sesión → redirige a /usuarios/login/
    Si el rol no está permitido → redirige al home.
    """
    allowed = {r.lower() for r in allowed_roles}

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            vecino_id = request.session.get("vecino_id")
            if not vecino_id:
                return redirect('usuarios_login')

            try:
                vecino = Vecino.objects.select_related('id_rol').get(pk=vecino_id)
            except Vecino.DoesNotExist:
                messages.error(request, "Tu sesión no es válida.")
                return redirect('usuarios_login')

            rol_nombre = (vecino.id_rol.nombre or '').strip().lower()
            if rol_nombre not in allowed:
                messages.error(request, "No tienes permiso para acceder a esta sección.")
                return redirect('home')

            request.vecino = vecino
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
