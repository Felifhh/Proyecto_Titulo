from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import os

from .models import Certificado
from Usuarios.models import Vecino
from .utils import generar_folio, generar_qr
from .forms import SolicitudCertificadoForm
from django.shortcuts import get_object_or_404
import requests
from transbank.webpay.webpay_plus.transaction import Transaction
from django.urls import reverse
from Usuarios.decorators import require_role
from Auditoria.utils import registrar_evento

def notificar_n8n(evento, datos):
    webhook_url = "https://felifhhhh.app.n8n.cloud/webhook/Correo-Mensaje"  # URL definitiva
    try:
        requests.post(webhook_url, json={"evento": evento, **datos}, timeout=5)
        print(f" Evento '{evento}' enviado correctamente a n8n.")
    except Exception as e:
        print(f" Error enviando evento a n8n: {e}")


# ========================================================
# SOLICITAR CERTIFICADO (Vecino)
# ========================================================
def solicitar_certificado(request):
    vecino_id = request.session.get("vecino_id")
    if not vecino_id:
        messages.error(request, "Debes iniciar sesión para solicitar un certificado.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=vecino_id)
    ahora = timezone.now()
    DURACION_CERTIFICADO = timedelta(days=30)

    # Verificar certificado vigente
    cert_existente = Certificado.objects.filter(
        id_vecino=vecino, tipo="Residencia"
    ).order_by('-fecha_emision').first()

    if cert_existente and cert_existente.estado == "Emitido" and cert_existente.fecha_emision:
        if cert_existente.fecha_emision + DURACION_CERTIFICADO > ahora:
            messages.info(request, "Ya tienes un certificado vigente emitido hace menos de 30 días.")
            return render(request, "Certificados/certificado_detalle.html", {"certificado": cert_existente, "vecino": vecino})

    if Certificado.objects.filter(id_vecino=vecino, tipo="Residencia", estado="Pendiente").exists():
        messages.warning(request, "Ya tienes una solicitud pendiente.")
        return redirect("mis_certificados")

    if request.method == "POST":
        form = SolicitudCertificadoForm(request.POST)
        if form.is_valid():
            amount = 1500
            buy_order = f"CERT-{vecino.id_vecino}-{int(timezone.now().timestamp())}"
            session_id = request.session.session_key or str(vecino.id_vecino)
            return_url = request.build_absolute_uri(reverse("retorno_pago_certificado"))

            tx = Transaction()
            tx.configure_for_testing()
            response = tx.create(buy_order, session_id, amount, return_url)

            request.session["certificado_pago"] = {
                "vecino_id": vecino.id_vecino, 
                "tipo": "Residencia",
                "amount": amount,
                "token": response["token"],
            }

            registrar_evento(request, f"Solicitud de certificado de residencia iniciada (pago pendiente)", "Éxito")

            return render(request, "pagos/iniciar_pago.html", {"url": response["url"], "token": response["token"]})
    else:
        form = SolicitudCertificadoForm()

    return render(request, "Certificados/solicitar_certificado.html", {"form": form})



# ========================================================
# REVISAR CERTIFICADOS (Directiva)
# ========================================================
@require_role(['presidente', 'secretario', 'tesorero'])
def revisar_certificados(request):
    certificados = Certificado.objects.filter(tipo="Residencia").order_by('-id_certificado')
    return render(request, "Certificados/revisar_certificados.html", {"certificados": certificados})


# ========================================================
# APROBAR CERTIFICADO
# ========================================================
@require_role(['presidente', 'secretario', 'tesorero'])
def aprobar_certificado(request, id_certificado):
    cert = get_object_or_404(Certificado, pk=id_certificado)

    if cert.estado != "Pendiente":
        messages.warning(request, "Este certificado ya fue procesado.")
        return redirect("revisar_certificados")

    folio = generar_folio()
    qr_rel_path = generar_qr(folio)
    qr_url = f"{settings.MEDIA_URL}{qr_rel_path}"

    cert.folio = folio
    cert.qr_code = qr_url
    cert.estado = "Emitido"
    cert.fecha_emision = timezone.now()
    cert.save()

    registrar_evento(request, f"Aprobación del certificado de residencia (Folio: {folio})", "Éxito")

    vecino = cert.id_vecino
    notificar_n8n("documento_aceptado", {
        "nombre": vecino.nombre,
        "correo": vecino.correo,
        "run": vecino.run
    })

    messages.success(request, f"Certificado de {vecino.nombre} emitido correctamente.")
    return redirect("revisar_certificados")


# ========================================================
# RECHAZAR CERTIFICADO
# ========================================================
@require_role(['presidente', 'secretario', 'tesorero'])
def rechazar_certificado(request, id_certificado):
    cert = get_object_or_404(Certificado, pk=id_certificado)

    if cert.estado != "Pendiente":
        messages.warning(request, "Este certificado ya fue procesado.")
        return redirect("revisar_certificados")

    cert.estado = "Rechazado"
    cert.fecha_emision = timezone.now()
    cert.save()

    registrar_evento(request, f"Rechazo de certificado de residencia del vecino '{cert.id_vecino.nombre}'", "Éxito")

    vecino = cert.id_vecino
    notificar_n8n("documento_rechazado", {
        "nombre": vecino.nombre,
        "correo": vecino.correo,
        "run": vecino.run
    })

    messages.error(request, f"Solicitud de {vecino.nombre} rechazada.")
    return redirect("revisar_certificados")


# ========================================================
# MIS CERTIFICADOS (Vecino)
# ========================================================
def mis_certificados(request):
    if not request.session.get("vecino_id"):
        messages.error(request, "Debes iniciar sesión para ver tus certificados.")
        return redirect("home")

    vecino = get_object_or_404(Vecino, pk=request.session["vecino_id"])
    certificados = Certificado.objects.filter(id_vecino=vecino, tipo="Residencia").order_by('-id_certificado')

    return render(request, "Certificados/mis_certificados.html", {"certificados": certificados})


# ========================================================
# VER CERTIFICADO
# ========================================================
def ver_certificado(request, id_certificado):
    cert = get_object_or_404(Certificado, pk=id_certificado)
    if cert.estado != "Emitido":
        messages.error(request, "Tu certificado aún no ha sido emitido por la directiva.")
        return redirect("mis_certificados")

    registrar_evento(request, f"Visualización del certificado (Folio: {cert.folio})", "Éxito")
    return render(request, "Certificados/ver_certificado.html", {"certificado": cert})


# ---------------------------
# NUEVA FUNCIÓN PARA DESCARGAR COMO PDF
# ---------------------------

import io
import os
from django.conf import settings
from django.http import FileResponse
from django.contrib import messages
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from .models import Certificado


def descargar_certificado_pdf(request, folio):
    vecino_id = request.session.get("vecino_id")
    if not vecino_id:
        messages.error(request, "Debes iniciar sesión para descargar tu certificado.")
        return redirect("home")

    try:
        certificado = Certificado.objects.get(folio=folio)
        vecino = certificado.id_vecino
    except Certificado.DoesNotExist:
        messages.error(request, "Certificado no encontrado.")
        return redirect("home")

    # Crear buffer de memoria
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Colores y tipografía base
    color_texto = HexColor("#555555")
    color_titulo = HexColor("#333333")
    p.setFillColor(color_texto)

    # Margen superior
    y = height - 3 * cm

    # --- Encabezado ---
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(color_titulo)
    p.drawCentredString(width / 2, y, "CERTIFICADO DE RESIDENCIA")
    y -= 1 * cm

    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, y, "JUNTA DE VECINOS LOS HIDALGOS")
    y -= 2 * cm
    p.setFillColor(color_texto)

    # --- Datos del certificado ---
    p.setFont("Helvetica", 11)
    p.drawRightString(width - 3 * cm, y, f"FOLIO: {certificado.folio}")
    y -= 0.8 * cm

    fecha = certificado.fecha_emision.strftime("%d DE %B, %Y").upper()
    p.drawRightString(width - 3 * cm, y, f"BUIN, {fecha}")
    y -= 1.2 * cm

    p.drawString(3 * cm, y, f"CERTIFICA QUE DON(ÑA): {vecino.nombre}")
    y -= 1 * cm
    p.drawString(3 * cm, y, f"RUN: {vecino.run}")
    y -= 1 * cm
    p.drawString(3 * cm, y, f"DOMICILIADO(A) EN: {vecino.direccion}")
    y -= 1 * cm
    p.drawString(3 * cm, y, "SE EXTIENDE EL PRESENTE CERTIFICADO PARA SER PRESENTADO CON FINES")
    y -= 0.6 * cm
    p.drawString(3 * cm, y, "QUE ESTE ESTIME CONVENIENTE.")
    y -= 1 * cm
    p.drawString(3 * cm, y, "ESTE DOCUMENTO TIENE UNA VALIDEZ DE 30 DÍAS A CONTAR DE LA FECHA")
    y -= 0.6 * cm
    p.drawString(3 * cm, y, "DE EMISIÓN, PASADA LA FECHA NO HAY RESPONSABILIDAD DE QUIEN EMITE")
    y -= 2.5 * cm
    p.drawString(3 * cm, y, "EL CERTIFICADO.")
    y -= 0.6 * cm

    # --- Firmas ---
    p.setFont("Helvetica", 11)

    # Coordenadas base de las firmas
    firma_y = y  # posición vertical común para ambas firmas
    firma_secretario_x = 3 * cm
    firma_presidente_x = width - 8 * cm

    # Rutas absolutas de las imágenes de firmas
    firma_secretario_path = os.path.join(settings.MEDIA_ROOT, "firmas", "firma_secretaria.jpg")
    firma_presidente_path = os.path.join(settings.MEDIA_ROOT, "firmas", "firma_presidente.jpg")

    # Tamaño estándar para las firmas (ajustable)
    firma_width = 4 * cm
    firma_height = 2 * cm

    # Dibujar firmas si existen
    if os.path.exists(firma_secretario_path):
        p.drawInlineImage(firma_secretario_path, firma_secretario_x, firma_y, firma_width, firma_height)
    if os.path.exists(firma_presidente_path):
        p.drawInlineImage(firma_presidente_path, firma_presidente_x, firma_y, firma_width, firma_height)

    # Texto bajo las firmas
    p.setFont("Helvetica", 11)
    p.drawCentredString(firma_secretario_x + (firma_width / 2), firma_y - 0.5 * cm, "SECRETARIO")
    p.drawCentredString(firma_presidente_x + (firma_width / 2), firma_y - 0.5 * cm, "PRESIDENTE")

    # Ajustar espacio inferior antes del QR
    y = firma_y - 3.5 * cm


    # --- QR Code ---
    if certificado.qr_code:
        qr_path = certificado.qr_code.replace(settings.MEDIA_URL, '')
        qr_path = os.path.join(settings.MEDIA_ROOT, qr_path)
        if os.path.exists(qr_path):
            qr_size = 4 * cm
            p.drawInlineImage(qr_path, (width - qr_size) / 2, y - qr_size, qr_size, qr_size)
            y -= qr_size + 1 * cm

    # --- Texto final ---
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(color_texto)
    p.drawCentredString(width / 2, y, "Validez: 30 días desde la fecha de emisión.")
    y -= 0.6 * cm
    p.drawCentredString(width / 2, y, "Este documento acredita residencia del vecino dentro de la Junta Vecinal.")

    # Guardar PDF
    p.showPage()
    p.save()
    buffer.seek(0)

    filename = f"{certificado.folio}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)
