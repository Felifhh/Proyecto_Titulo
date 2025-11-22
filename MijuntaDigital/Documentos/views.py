from django.conf import settings
import json
from google.cloud import vision
import io
import os

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from MijuntaDigital.settings import get_gcp_credentials
from Usuarios.decorators import require_role
from .models import Documento
from .forms import DocumentoForm
from django.db.models import Q
import requests

from google.cloud import vision



# ===============================================

@require_role(["presidente", "secretario", "tesorero", "vecino"])
def lista_documentos(request):
    query = request.GET.get("buscar", "").strip()

    vecino_id = request.session.get("vecino_id")
    documentos = Documento.objects.filter(id_vecino_id=vecino_id).order_by("-fecha_subida")

    # Búsqueda universal (título + tipo + descripción + OCR)
    if query:
        documentos = documentos.filter(
            Q(titulo__icontains=query) |
            Q(tipo__icontains=query) |
            Q(texto_extraido__icontains=query)
        )

    return render(request, "Documentos/lista_documentos.html", {
        "documentos": documentos,
        "query": query,
    })


@require_role(["presidente", "secretario", "tesorero", "vecino"])
@require_http_methods(["GET", "POST"])
def subir_documento(request):
    """
    Permite subir un documento. Aplica OCR si es imagen o PDF.
    """
    if request.method == "POST":
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.id_vecino_id = request.session.get("vecino_id")
            documento.save()

            aplicar_ocr(documento)

            messages.success(request, "Documento subido correctamente con OCR aplicado.")
            return redirect("lista_documentos")
        else:
            messages.error(request, "Error al subir el documento. Revisa los campos.")
    else:
        form = DocumentoForm()
    return render(request, "Documentos/subir_documento.html", {"form": form})


@require_role(["presidente", "secretario", "tesorero", "vecino"])
def detalle_documento(request, id_documento):
    """
    Muestra el detalle del documento junto con el texto OCR extraído.
    Detecta si es imagen para mostrar vista previa.
    """
    documento = get_object_or_404(Documento, pk=id_documento)
    
    # Detectar si el archivo es imagen
    url = documento.archivo.url.lower()
    es_imagen = url.endswith(".jpg") or url.endswith(".jpeg") or url.endswith(".png") or url.endswith(".webp")

    return render(request, "Documentos/detalle_documento.html", {
        "documento": documento,
        "es_imagen": es_imagen
    })


# ===============================================
# OCR automático
# ===============================================

def aplicar_ocr(documento):
    """
    Aplica OCR usando Google Cloud Vision API.
    """
    try:
        # 1) Cargar credenciales desde Supabase
        creds = get_gcp_credentials()
        if not creds:
            raise Exception("No se pudieron cargar credenciales GCP.")

        # 2) Crear cliente de Google Vision usando tus credenciales
        client = vision.ImageAnnotatorClient.from_service_account_info(creds)

        file_path = documento.archivo.path

        with io.open(file_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            documento.texto_extraido = texts[0].description.strip()
        else:
            documento.texto_extraido = "(No se detectó texto)"

        documento.save()

        if response.error.message:
            raise Exception(response.error.message)

    except Exception as e:
        print(f"[Google OCR ERROR] {e}")
        documento.texto_extraido = f"(Error OCR: {e})"
        documento.save()

