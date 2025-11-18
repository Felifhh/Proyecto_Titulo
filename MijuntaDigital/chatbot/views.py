from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from Usuarios.models import Vecino

import google.generativeai as genai
import traceback
import json
import os
import logging
import re
from datetime import datetime, date, timedelta

# Models for DB-driven responses
from Reserva.models import EspacioComunal, Reserva
from Actividades.models import Actividad
from django.views.decorators.http import require_POST
from django.db import transaction
from django.shortcuts import get_object_or_404
from Auditoria.utils import registrar_evento
from Reserva.views import iniciar_pago_reserva
from django.urls import reverse
from django.shortcuts import render
from django.utils.html import escape

logger = logging.getLogger(__name__)



# ==========================================================
# CONFIGURACIÓN GEMINI
# ==========================================================

# Cargar API key desde entorno (.env)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Indicador global
GEMINI_ENABLED = False

if GEMINI_API_KEY:
    try:
        # Configurar Gemini (seguro en settings.py)
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_ENABLED = True
    except Exception as e:
        logger.exception("No se pudo configurar Gemini con la API key proporcionada.")
else:
    logger.warning("Gemini API key no encontrada. Gemini deshabilitado; se usará fallback local.")


# Ruta a los KB locales
KB_DIR = os.path.join(os.path.dirname(__file__), "kb")

# ==========================================================
# FUNCIÓN PRINCIPAL DEL CHATBOT
# ==========================================================
@csrf_exempt
def chatbot_api(request):
    mensaje = request.GET.get("mensaje", "").strip()
    if not mensaje:
        return JsonResponse({"respuesta": "Por favor, escribe un mensaje."})

    lower = mensaje.lower().strip()
    vecino_id = request.session.get("vecino_id")
    vecino_rol = request.session.get("vecino_rol", "").lower()

    # Determinar perfil del usuario (se utilizará en el prompt para Gemini)
    if not vecino_id:
        perfil = "invitado"
        contexto_usuario = (
            "El usuario no está autenticado. "
            "Explícale de forma amable y general qué es Mi Junta Digital, qué beneficios tiene registrarse, "
            "y qué tipo de gestiones podrá hacer al iniciar sesión."
        )
    else:
        try:
            vecino = Vecino.objects.get(pk=vecino_id)
            if vecino_rol in ["presidente", "secretario", "tesorero"]:
                perfil = "directorio"
                contexto_usuario = (
                    f"El usuario pertenece al Directorio. y  su nombre es {vecino.nombre} su rol es {vecino_rol}. "
                    "Debe poder consultar información sobre actividades, certificados, noticias, reservas, documentos, mis_reservas, solicitudes, proyectos. "
                    "Debe poder consultar información sobre gestiones administrativas como gestión de usuarios, gestión de espacios, solicitudes de certificados, gestión de proyectos, gestión de solicitudes ciudadanas, auditoría y métricas. "
                    "Responde de forma clara y profesional, sin inventar funciones no existentes."
                )
            else:
                perfil = "vecino"
                contexto_usuario = (
                    f"El usuario está autenticado como vecino, su nombre es {vecino.nombre}. "
                    "Debe poder consultar información sobre actividades, certificados, noticias, reservas, documentos, mis_reservas, solicitudes, proyectos. "
                    "Responde de forma cordial y solo con información accesible para vecinos."
                )
        except Vecino.DoesNotExist:
            perfil = "invitado"
            contexto_usuario = (
                "El usuario no está autenticado correctamente. "
                "Explícale qué puede hacer al iniciar sesión."
            )

    # Atajos permitidos: 'mis reservas'
    try:
        if re.search(r"\b(mis reservas|ver mis reservas|tus reservas)\b", lower):
            if not vecino_id:
                return JsonResponse({"respuesta": "Debes iniciar sesión para ver tus reservas. Usa la sección 'Mis Reservas' después de iniciar sesión."})
            return JsonResponse({"respuesta": "Puedes ver tus reservas en la sección 'Mis Reservas' del sitio. Si quieres, puedo mostrarte las disponibles para cierta fecha."})
    except Exception:
        pass

    # ==========================================================
    # Comando: mostrar actividades activas (lista ordenada)
    # ==========================================================
    try:
        if re.search(r"\b(ver|mostrar|me puedes mostrar)\b.*\bactividades\b", lower):
            actividades = Actividad.objects.filter(estado="Activa").order_by("fecha", "hora_inicio")

            if not actividades.exists():
                return JsonResponse({"respuesta": "No hay actividades activas en este momento."})

            # Construir texto tipo lista ordenada y legible
            texto = " <strong>Actividades activas:</strong><br><br><ul>"
            for a in actividades:
                fecha = a.fecha.strftime("%d-%m-%Y") if a.fecha else "(sin fecha)"
                hi = a.hora_inicio.strftime("%H:%M") if a.hora_inicio else "--:--"
                hf = a.hora_fin.strftime("%H:%M") if a.hora_fin else "--:--"
                lugar = escape(a.ubicacion or "(sin ubicación)")
                desc = (a.descripcion[:120] + "...") if a.descripcion and len(a.descripcion) > 120 else (a.descripcion or "Sin descripción")

                texto += (
                    f"<li><strong>{escape(a.titulo)}</strong><br>"
                    f" {fecha} —  {hi}-{hf}<br>"
                    f" {lugar}<br>"
                    f" {escape(desc)}</li><br>"
                )

            texto += "</ul>"
            return JsonResponse({"respuesta": texto})

    except Exception as e:
        logger.exception("Error listando actividades activas desde chatbot: %s", e)
        return JsonResponse({"respuesta": "Ocurrió un error al obtener las actividades. Intenta nuevamente más tarde."})

    # ==========================================================
    #  Comando : ver espacios disponibles (formato lista)
    # ==========================================================
    if lower == "quiero ver espacios disponibles":
        target = detectar_fecha(mensaje)
        espacios = espacios_disponibles(target)

        # Si no hay resultados
        if not espacios:
            if target:
                fecha_txt = target.strftime("%Y-%m-%d")
                texto_disp = f"No hay espacios comunales disponibles para el {fecha_txt}."
            else:
                texto_disp = "No hay espacios comunales disponibles en este momento."
            return JsonResponse({"respuesta": texto_disp})

        # Construcción del texto con formato de lista HTML
        texto = (
            " <strong>Espacios comunales disponibles</strong>"
            + (f" para el {target.strftime('%Y-%m-%d')}" if target else "")
            + ":<br><br><ul>"
        )

        for idx, e in enumerate(espacios, start=1):
            desc = (e.descripcion[:120] + "...") if e.descripcion and len(e.descripcion) > 120 else (e.descripcion or "Sin descripción")
            monto_fmt = f"${e.monto_hora:,}" if isinstance(e.monto_hora, (int, float)) else str(e.monto_hora)
            nombre = escape(e.nombre)
            texto += (
                f"<li><strong>{idx}. {nombre}</strong><br>"
                f" {escape(desc)}<br>"
                f" {monto_fmt}/hora</li><br>"
            )

        texto += "</ul>"

        return JsonResponse({"respuesta": texto})


    # ==========================================================
    # 2) Comando que empieza con 'reservar ' -> crear reserva tentativa
    #    (formato esperado: 'reservar <nombre o id> YYYY-MM-DD HH:MM-HH:MM')
    # ==========================================================
    if lower.startswith("reservar "):
        if not vecino_id:
            return JsonResponse({"respuesta": "Debes iniciar sesión para crear una reserva. Inicia sesión y vuelve a intentar."})

        # extraer fecha, horario y espacio del texto
        fecha = _fecha_desde_texto(mensaje)
        hora_inicio, hora_fin = _extraer_horario(mensaje)
        espacio = _buscar_espacio_por_texto(mensaje)

        if not espacio:
            return JsonResponse({"respuesta": "No pude identificar el espacio. Indica el nombre exacto del espacio (por ejemplo: 'Parque') o usa el id después de 'reservar'."})
        if not fecha or not hora_inicio or not hora_fin:
            return JsonResponse({"respuesta": "Para reservar un espacio, debes escribir: 'reservar (nombre) (fecha) (hora inicio(00:00) hasta hora fin(00:00))'"})

        # comprobar conflictos
        conflict = _horario_conflict(espacio, fecha, hora_inicio, hora_fin)
        if conflict:
            return JsonResponse({"respuesta": f"El espacio '{espacio.nombre}' no está disponible el {fecha.strftime('%Y-%m-%d')} de {hora_inicio} a {hora_fin}."})

        # Guardar tentativa en sesión
        request.session["tentative_reservation"] = {
            "espacio_id": espacio.pk,
            "fecha": fecha.strftime("%Y-%m-%d"),
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
        }
        request.session.modified = True
        return JsonResponse({"respuesta": f"Reserva tentativa creada para '{espacio.nombre}' el {fecha.strftime('%Y-%m-%d')} de {hora_inicio} a {hora_fin}. Responde 'confirmar reserva' para iniciar el pago."})

    # ==========================================================
    # 3) Confirmar reserva (iniciar pago)
    # ==========================================================
    if lower == "confirmar reserva" or lower == "confirmar":
        if not vecino_id:
            return JsonResponse({"respuesta": "Debes iniciar sesión para confirmar una reserva."})
        tentative = request.session.get("tentative_reservation")
        if not tentative:
            return JsonResponse({"respuesta": "No hay ninguna reserva tentativa para confirmar."})
        try:
            response = iniciar_pago_reserva(request, vecino_id, tentative["espacio_id"], tentative["fecha"], tentative["hora_inicio"], tentative["hora_fin"])
            redirect_url = request.build_absolute_uri(reverse('chatbot_abrir_pago'))
            return JsonResponse({
                                "respuesta": (
                                    "<p>He generado la página de pago.</p>"
                                    "<a href='{url}' "
                                    "style='display:inline-block;padding:10px 18px;background:#007bff;"
                                    "color:white;border-radius:6px;text-decoration:none;font-weight:bold;'>"
                                    "Abrir aquí"
                                    "</a>"
                                ).format(url=redirect_url)
                            })
        except Exception as e:
            logger.exception("Error iniciando pago desde chatbot: %s", e)
            return JsonResponse({"respuesta": f"No se pudo iniciar el pago: {e}"})

    # ==========================================================
    # 4) Por defecto: usar Gemini (si está) o fallback KB para responder
    #    Recordatorio dentro del prompt: indicar al usuario las frases exactas
    # ==========================================================
    kb_texto = ""
    for archivo in [
    "actividades.json", "certificados.json", "noticias.json", "reservas.json",
    "documentos.json", "mis_reservas.json", "solicitudes.json", "proyectos.json",
    "solicitudes_registro.json", "gestion_usuarios.json", "gestion_espacios.json",
    "solicitudes_certificados.json", "gestion_proyectos.json",
    "gestion_solicitudes_ciudadanas.json", "auditoria_metricas.json"
]:
        kb_texto += "\n\n" + cargar_kb(archivo)


    try:
        if GEMINI_ENABLED:
            model = genai.GenerativeModel("models/gemini-2.0-flash")
            # Si detectamos intención de reserva, no incluimos la instrucción que
            # fuerza la respuesta "Solo puedo responder..."; en su lugar pedimos
            # al modelo que sea colaborativo y ayude con pasos para reservar.
            # Instrucciones sobre frases trigger que el usuario debe usar para
            # ejecutar acciones del sistema.
            trigger_instructions = (
                "Si el usuario desea ver la lista de espacios, pídele que escriba exactamente: 'quiero ver espacios disponibles'. "
                "Si desea crear una reserva, indícale que use la forma: 'reservar (nombre) (fecha) (hora inicio hasta hora fin)'. "
                "Solo cuando el usuario escriba esas frases en específico, el sistema "
                "ejecutará la acción correspondiente (mostrar lista o crear reserva tentativa)."
            )

            extra_instruction = (
                "El usuario ha usado la frase de reserva; responde de forma colaborativa, "
                "guiándolo en los pasos necesarios para completar la reserva, pidiendo aclaraciones "
                "si faltan datos (espacio, fecha, hora) y evitando la frase 'Solo puedo responder preguntas sobre Mi Junta Digital.'"
                )
            extra_instruction = (
                    "Si la consulta es ajena, responde: 'Solo puedo responder preguntas sobre Mi Junta Digital.'"
                )

            prompt = f"""
Eres un asistente virtual llamado "Asistente Mi Junta Digital".
Tu función es ayudar a los vecinos a resolver consultas sobre la plataforma Mi Junta Digital.
Usa HTML simple (<p>, <ul>, <li>, <strong>) para que las respuestas sean ordenadas no muy largas.
Nunca incluyas código ni scripts.
{extra_instruction}
{trigger_instructions}
Usa la siguiente información de contexto para responder con precisión y profesionalismo.

Perfil del usuario: {perfil}
Contexto: {contexto_usuario}

Base de conocimiento (referencia interna):
{kb_texto}

Mensaje del usuario:
{mensaje}

Responde en un formato claro, ordenado y con tono amable.
"""
            respuesta = model.generate_content(prompt)
            texto = respuesta.text.strip()
        else:
            raise Exception("Gemini no configurado")
    except Exception as e:
        logger.exception("Gemini error o no configurado: %s", e)
        kb_snippet = buscar_en_kb(mensaje)
        if kb_snippet:
            texto = f"No pude procesar la respuesta con el servicio externo, pero encontré esto en la base de conocimiento:\n\n{kb_snippet}"
        else:
            texto = "Ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente más tarde o formula la pregunta de otra manera."

    return JsonResponse({"respuesta": texto})

def cargar_kb(nombre_archivo):
    """Carga un archivo KB del directorio /kb."""
    try:
        ruta = os.path.join(KB_DIR, nombre_archivo)
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f" No se pudo cargar {nombre_archivo}: {e}")
        return ""


def detectar_fecha(text):
    """Detecta palabras clave de fecha simples: 'hoy', 'mañana' o YYYY-MM-DD."""
    txt = (text or "").lower()
    if "hoy" in txt:
        return date.today()
    if "mañana" in txt or "manana" in txt:
        return date.today() + timedelta(days=1)

    # intentar detectar YYYY-MM-DD
    try:
        for part in txt.split():
            if "-" in part and len(part) >= 8:
                try:
                    return datetime.strptime(part, "%Y-%m-%d").date()
                except Exception:
                    continue
    except Exception:
        pass
    return None


def espacios_disponibles(target_date=None):
    """Devuelve una lista de espacios comunales disponibles.

    Si target_date es None, devuelve todos los espacios activos.
    Si se especifica fecha, excluye los espacios con reserva activa en esa fecha.
    """
    try:
        espacios = EspacioComunal.objects.filter(estado="Activo")
        if target_date:
            reserved_ids = Reserva.objects.filter(fecha=target_date, estado__in=["Activa", "Confirmada"]).values_list("id_espacio", flat=True)
            espacios = espacios.exclude(pk__in=list(reserved_ids))
        return list(espacios)
    except Exception as e:
        logger.exception("Fallo consultando espacios disponibles: %s", e)
        return []


def _buscar_espacio_por_texto(text):
    """Intento simple de mapear un texto libre a un `EspacioComunal` activo.
    Busca coincidencias por nombre (contains, case-insensitive) y devuelve
    el primer resultado encontrado o None.
    """
    try:
        texto = (text or "").lower()
        espacios = EspacioComunal.objects.filter(estado="Activo")
        # Evitar interpretar números que forman parte de una fecha (ej. 13-11-2025)
        texto_sin_fechas = re.sub(r"\b\d{1,2}-\d{1,2}-\d{4}\b", "", texto)
        texto_sin_fechas = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", texto_sin_fechas)
        # Si el usuario indica un id numérico aislado en el texto (no parte de una fecha), intentar obtener por PK
        m_id = re.search(r"\b(\d{1,6})\b", texto_sin_fechas)
        if m_id:
            try:
                candidato = EspacioComunal.objects.get(pk=int(m_id.group(1)), estado="Activo")
                return candidato
            except Exception:
                pass
        # Priorizar coincidencia completa del nombre
        for e in espacios:
            if e.nombre and e.nombre.lower() in texto:
                return e

        # Si no hay coincidencia completa, intentar por tokens
        tokens = [t for t in re.split(r"\W+", texto) if len(t) > 2]
        for t in tokens:
            for e in espacios:
                if e.nombre and t in e.nombre.lower():
                    return e
        return None
    except Exception:
        return None


def _extraer_horario(text):
    """Extrae un par (hora_inicio_str, hora_fin_str) desde texto en formatos comunes.
    Ejemplos: '10:00 a 12:00', '10:00-12:00', 'de 10:00 a 12:00'.
    Devuelve (hora_inicio_str, hora_fin_str) o (None, None).
    """
    if not text:
        return None, None
    # Buscar patrón HH:MM ... HH:MM
    m = re.search(r"(\d{1,2}:\d{2})\s*(?:-|a|al|hasta|to|a las|a las)?\s*(\d{1,2}:\d{2})", text)
    if m:
        return m.group(1), m.group(2)
    return None, None


def _fecha_desde_texto(text):
    """Intenta detectar fecha usando `detectar_fecha` o patrón YYYY-MM-DD en el texto."""
    # Primera opción: usar la función existente
    f = detectar_fecha(text)
    if f:
        return f
    # Intentar extraer YYYY-MM-DD o DD-MM-YYYY
    m = re.search(r"(\d{4}-\d{2}-\d{2}|\d{1,2}-\d{1,2}-\d{4})", text)
    if m:
        s = m.group(1)
        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
        return None
    return None


def _horario_conflict(espacio, fecha, hora_inicio_str, hora_fin_str):
    """Comprueba si existe conflicto de horarios para un espacio en una fecha dada."""
    try:
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        hi = datetime.strptime(hora_inicio_str, "%H:%M").time()
        hf = datetime.strptime(hora_fin_str, "%H:%M").time()
        return Reserva.objects.filter(
            id_espacio=espacio,
            fecha=fecha,
            estado__in=["Activa", "Aprobada", "Pendiente", "Confirmada"]
        ).filter(
            hora_inicio__lt=hf,
            hora_fin__gt=hi
        ).exists()
    except Exception:
        # Si no se puede parsear, asumimos conflicto para ser conservadores
        return True


def buscar_en_kb(mensaje):
    """Búsqueda simple en los archivos KB: devuelve el primer párrafo que contenga
    alguna de las palabras del mensaje o None si no se encuentra nada útil.
    Esto sirve como fallback cuando el modelo externo falla.
    """
    try:
        texto_kb = ""
        for archivo in ["actividades.json", "certificados.json", "noticias.json", "reservas.json", "documentos.json","mis_reservas.json","solicitudes.json"]:
            texto_kb += "\n\n" + cargar_kb(archivo)

        tokens = [t.lower() for t in re.split(r"\W+", mensaje) if len(t) > 3]
        for t in tokens:
            idx = texto_kb.lower().find(t)
            if idx != -1:
                # devolver 300 caracteres alrededor como snippet
                start = max(0, idx - 100)
                end = min(len(texto_kb), idx + 200)
                return texto_kb[start:end].strip()
    except Exception:
        return None
    return None





@csrf_exempt
def abrir_pago(request):
    """Renderiza la plantilla de inicio de pago usando los datos guardados en session['reserva_pago'].
    Esto replica exactamente lo que hace `reservar_desde_catalogo` al mostrar el botón que POSTea a Transbank.
    """
    data = request.session.get("reserva_pago")
    if not data:
        return JsonResponse({"respuesta": "No hay una transacción de pago pendiente en la sesión."}, status=400)

    payment_url = data.get("payment_url")
    token = data.get("payment_token")
    if not payment_url or not token:
        return JsonResponse({"respuesta": "Faltan datos de la transacción de pago."}, status=400)

    # Renderizar la plantilla que contiene el formulario POST a Transbank
    return render(request, "pagos/iniciar_pago.html", {"url": payment_url, "token": token})


def _calcular_total_por_horas(espacio, hora_inicio, hora_fin):
    """Calcula el total dado el precio por hora del espacio y horas de inicio/fin (time objects)."""
    try:
        dt_start = datetime.combine(date.today(), hora_inicio)
        dt_end = datetime.combine(date.today(), hora_fin)
        horas = (dt_end - dt_start).total_seconds() / 3600
        if horas <= 0:
            return None
        return int(horas * (espacio.monto_hora or 0))
    except Exception:
        return None


def reservar_espacio(vecino_id, espacio_id, fecha, hora_inicio_str, hora_fin_str, creado_por="chatbot"):
    """Intentar crear una reserva de forma atómica. Devuelve (ok, mensaje, reserva_or_none)."""
    try:
        # Normalizar inputs
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
        hora_fin = datetime.strptime(hora_fin_str, "%H:%M").time()

        vecino = get_object_or_404(Vecino, pk=vecino_id)
        espacio = get_object_or_404(EspacioComunal, pk=espacio_id, estado="Activo")

        with transaction.atomic():
            # Lock espacio row to avoid races
            EspacioComunal.objects.select_for_update().get(pk=espacio.pk)

            # comprobar solapamientos
            conflict = Reserva.objects.filter(
                id_espacio=espacio,
                fecha=fecha,
                estado__in=["Activa", "Aprobada", "Pendiente"]
            ).filter(
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio
            ).exists()

            if conflict:
                return False, "El espacio no está disponible en ese horario.", None

            total = _calcular_total_por_horas(espacio, hora_inicio, hora_fin)
            if total is None:
                return False, "Horas inválidas proporcionadas.", None

            reserva = Reserva.objects.create(
                id_vecino=vecino,
                id_espacio=espacio,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                estado="Aprobada",
                total=total,
            )

            registrar_evento(None, f"Reserva automática por chatbot: {vecino.nombre} - {espacio.nombre}", "Éxito")
            return True, "Reserva realizada correctamente.", reserva

    except Exception as e:
        logger.exception("Error creando reserva por chatbot: %s", e)
        registrar_evento(None, f"Error reserva chatbot: {e}", "Error")
        return False, f"Error técnico: {e}", None


@require_POST
@csrf_exempt
def crear_reserva_tentativa(request):
    """Crea una reserva tentativa en la sesión. Espera JSON con espacio_id, fecha (YYYY-MM-DD), hora_inicio (HH:MM), hora_fin (HH:MM)."""
    vecino_id = request.session.get("vecino_id")
    if not vecino_id:
        return JsonResponse({"ok": False, "msg": "Debes iniciar sesión para crear una reserva."}, status=403)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "msg": "JSON inválido."}, status=400)

    espacio_id = data.get("espacio_id")
    fecha = data.get("fecha")
    hora_inicio = data.get("hora_inicio")
    hora_fin = data.get("hora_fin")

    if not all([espacio_id, fecha, hora_inicio, hora_fin]):
        return JsonResponse({"ok": False, "msg": "Faltan parámetros. Se requiere espacio_id, fecha, hora_inicio, hora_fin."}, status=400)

    # Guardar en sesión
    request.session["tentative_reservation"] = {
        "espacio_id": espacio_id,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
    }
    request.session.modified = True

    return JsonResponse({"ok": True, "msg": "Reserva tentativa creada. Confirma con POST a /chatbot/reservar/confirmar/ o envía 'confirmar reserva' en el chat."})


@require_POST
@csrf_exempt
def confirmar_reserva(request):
    """Confirma la reserva tentativa almacenada en sesión y la crea en la BD."""
    vecino_id = request.session.get("vecino_id")
    if not vecino_id:
        return JsonResponse({"ok": False, "msg": "Debes iniciar sesión para confirmar."}, status=403)

    tentative = request.session.get("tentative_reservation")
    if not tentative:
        return JsonResponse({"ok": False, "msg": "No hay reservas en sesión."}, status=400)

    ok, msg, reserva = reservar_espacio(
        vecino_id,
        tentative["espacio_id"],
        tentative["fecha"],
        tentative["hora_inicio"],
        tentative["hora_fin"]
    )

    if ok:
        # limpiar tentative
        request.session.pop("tentative_reservation", None)

        # Construir botón de acción con enlace al pago
        link_pago = request.build_absolute_uri(reverse('chatbot_abrir_pago'))
        boton_html = (
            f"<p>{msg}</p>"
            f"<p><a href='{link_pago}' target='_blank' "
            f"style='display:inline-block;padding:10px 20px;"
            f"background-color:#007bff;color:#fff;border-radius:6px;"
            f"text-decoration:none;font-weight:bold;'> Presiona aquí para continuar al pago</a></p>"
        )

        return JsonResponse({"ok": True, "msg": boton_html, "reserva_id": reserva.id_reserva})

    else:
        return JsonResponse({"ok": False, "msg": msg}, status=400)
