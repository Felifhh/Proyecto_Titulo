from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from Usuarios.models import Vecino

def require_role(allowed_roles):
    """
    Decorador que restringe acceso según el rol del usuario.
    Acepta string o lista de roles, y agrega 'request.vecino' al request.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    allowed = {r.lower() for r in allowed_roles}

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            vecino_id = request.session.get("vecino_id")
            vecino_rol = (request.session.get("vecino_rol") or "").lower()

            # Si no está autenticado
            if not vecino_id:
                messages.error(request, "Debes iniciar sesión para acceder a esta sección.")
                return redirect("home")

            # Si su rol no está permitido
            if vecino_rol not in allowed:
                messages.error(request, "No tienes permisos para acceder a esta sección.")
                return redirect("home")

            # ✅ Cargar el objeto del vecino autenticado
            request.vecino = get_object_or_404(Vecino, pk=vecino_id)
            request.vecino_rol = vecino_rol

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
