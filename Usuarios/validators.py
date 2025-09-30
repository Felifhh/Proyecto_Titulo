import re

# --- Validadores de RUN (ya los tenías) ---
def normalizar_run(run: str) -> str:
    run = run.replace('.', '').replace('-', '').strip().upper()
    return run

def formatear_run(run: str) -> str:
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
    run = normalizar_run(run)
    if not re.match(r'^\d{7,8}[0-9K]$', run):
        return False
    cuerpo, dv = run[:-1], run[-1]
    factores = [2,3,4,5,6,7]
    suma = 0
    for i, c in enumerate(reversed(cuerpo)):
        suma += int(c) * factores[i % len(factores)]
    resto = suma % 11
    dig = 11 - resto
    dv_calc = '0' if dig == 11 else 'K' if dig == 10 else str(dig)
    return dv_calc == dv

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
