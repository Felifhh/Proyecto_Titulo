from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import os

from .models import Certificado
from Usuarios.models import Vecino
from .utils import generar_folio, generar_qr


def solicitar_certificado(request):
    vecino_id = request.session.get("vecino_id")
    if not vecino_id:
        messages.error(request, "Debes iniciar sesión para solicitar un certificado.")
        return redirect("home")

    vecino = Vecino.objects.get(pk=vecino_id)
    ahora = timezone.now()
    DURACION_CERTIFICADO = timedelta(days=30)

    #  Buscar certificado del vecino
    cert_existente = Certificado.objects.filter(
        id_vecino=vecino,
        tipo="Residencia"
    ).first()

    # Si ya tiene un certificado vigente → mostrarlo directamente
    if cert_existente and cert_existente.fecha_emision and cert_existente.fecha_emision + DURACION_CERTIFICADO > ahora:
        messages.info(request, "Ya tienes un certificado vigente.")
        return render(
            request,
            "Certificados/certificado_detalle.html",
            {"certificado": cert_existente, "vecino": vecino}
        )

    # Si tenía uno vencido → borrar QR y registro anterior
    if cert_existente:
        if cert_existente.qr_code:
            old_path = cert_existente.qr_code.replace('/media/', '').replace('\\', '/')
            full_path = os.path.join(settings.MEDIA_ROOT, old_path)
            if os.path.isfile(full_path):
                os.remove(full_path)
        cert_existente.delete()

    #  Generar nuevo folio y QR
    folio = generar_folio()
    qr_rel_path = generar_qr(folio)  # ej: 'qr_codes/RES-20251007230141.png'
    qr_url = f"{settings.MEDIA_URL}{qr_rel_path}"

    # Crear el nuevo certificado
    certificado = Certificado.objects.create(
        id_vecino=vecino,
        tipo="Residencia",
        fecha_emision=ahora,
        folio=folio,
        qr_code=qr_url,
        estado="Emitido"
    )

    messages.success(request, "Certificado generado correctamente.")
    return render(
        request,
        "Certificados/certificado_detalle.html",
        {"certificado": certificado, "vecino": vecino}
    )



# ---------------------------
# NUEVA FUNCIÓN PARA DESCARGAR COMO PDF
# ---------------------------

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from django.http import FileResponse
import io
import os


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

    # Crear un buffer temporal en memoria
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Margen superior
    y = height - 3 * cm

    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "CERTIFICADO DE RESIDENCIA")
    y -= 1 * cm

    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, y, "JUNTA DE VECINOS MI JUNTA DIGITAL")
    y -= 2 * cm

    # Datos del certificado
    p.setFont("Helvetica", 11)
    p.drawString(3 * cm, y, f"Folio: {certificado.folio}")
    y -= 1 * cm
    p.drawString(3 * cm, y, f"Certifica que Don(ña): {vecino.nombre}")
    y -= 1 * cm
    p.drawString(3 * cm, y, f"RUN: {vecino.run}")
    y -= 1 * cm
    p.drawString(3 * cm, y, f"Domiciliado(a) en: {vecino.direccion}")
    y -= 1 * cm
    p.drawString(3 * cm, y, f"Fecha de emisión: {certificado.fecha_emision.strftime('%d/%m/%Y')}")
    y -= 1 * cm
    p.drawString(3 * cm, y, "Se extiende el presente certificado para ser presentado donde corresponda.")
    y -= 2 * cm

    # Firmas
    p.drawString(3 * cm, y, "__________________________")
    p.drawString(3 * cm, y - 0.5 * cm, "SECRETARIO")
    p.drawString(width - 8 * cm, y, "__________________________")
    p.drawString(width - 8 * cm, y - 0.5 * cm, "PRESIDENTE")

    y -= 3 * cm

    # Texto legal
    p.setFont("Helvetica-Oblique", 9)
    p.drawCentredString(width / 2, y, "Este documento tiene una validez de 30 días a contar de la fecha de emisión.")

    # Incluir el código QR si existe
    if certificado.qr_code:
        qr_path = certificado.qr_code.replace(settings.MEDIA_URL, '')
        qr_path = os.path.join(settings.MEDIA_ROOT, qr_path)
        if os.path.exists(qr_path):
            p.drawInlineImage(qr_path, width / 2 - 2 * cm, 3 * cm, 4 * cm, 4 * cm)

    # Guardar el PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    filename = f"{certificado.folio}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)
