import re
from django.core.exceptions import ValidationError
from .models import Vecino

# --- Validadores de RUN ---
def normalizar_run(run: str) -> str:
    """
    Limpia el RUN eliminando puntos y guiones, dejando solo dígitos y DV.
    """
    run = run.replace('.', '').replace('-', '').strip().upper()
    return run


def formatear_run(run: str) -> str:
    """
    Aplica formato estándar al RUN chileno: 12.345.678-9
    """
    run = normalizar_run(run)
    cuerpo, dv = run[:-1], run[-1]
    rev = ''.join(reversed(cuerpo))
    partes = []
    for i, c in enumerate(rev):
        if i and i % 3 == 0:
            partes.append('.')
        partes.append(c)
    cuerpo_fmt = ''.join(reversed(partes))
    return f"{cuerpo_fmt}-{dv}"


def validar_dv(run: str) -> bool:
    """
    Valida el dígito verificador (DV) del RUN chileno.
    """
    run = normalizar_run(run)
    if not re.match(r'^\d{7,8}[0-9K]$', run):
        return False
    cuerpo, dv = run[:-1], run[-1]
    factores = [2, 3, 4, 5, 6, 7]
    suma = 0
    for i, c in enumerate(reversed(cuerpo)):
        suma += int(c) * factores[i % len(factores)]
    resto = suma % 11
    dig = 11 - resto
    dv_calc = '0' if dig == 11 else 'K' if dig == 10 else str(dig)
    return dv_calc == dv


def validar_run_existente(run: str):
    """
    Verifica si el RUN ya existe en la base de datos y su estado.
    - Si está Pendiente -> mensaje de advertencia.
    - Si está Activo -> mensaje de error.
    - Si está Desactivado -> mensaje de contacto con la junta.
    """
    run = formatear_run(run)
    existente = Vecino.objects.filter(run=run).first()

    if existente:
        if existente.estado == 'Pendiente':
            raise ValidationError("Este RUN ya fue registrado y está pendiente de aprobación por la directiva.")
        elif existente.estado == 'Activo':
            raise ValidationError("Este RUN ya se encuentra activo en el sistema.")
        elif existente.estado == 'Desactivado':
            raise ValidationError("Este RUN fue desactivado. Contacte a su Junta Vecinal para su reactivación.")


# --- Validador de contraseña ---
def validar_contrasena(value: str) -> bool:
    """
    Debe tener al menos:
      - 1 mayúscula
      - 1 número
      - Longitud mínima 7
    """
    if len(value) < 7:
        return False
    if not re.search(r'[A-Z]', value):
        return False
    if not re.search(r'[0-9]', value):
        return False
    return True
