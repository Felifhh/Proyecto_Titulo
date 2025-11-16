from django.conf import settings
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(settings.BASE_DIR, "mijuntadigital-497d656bf8e0.json")
from google.cloud import vision
import io

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from Usuarios.decorators import require_role
from .models import Documento
from .forms import DocumentoForm
from django.db.models import Q



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
    Compatible con imágenes JPG, PNG y PDFs (limitado).
    """
    try:
        client = vision.ImageAnnotatorClient()
        file_path = documento.archivo.path
        extension = file_path.lower().split('.')[-1]

        with io.open(file_path, 'rb') as image_file:
            content = image_file.read()

        # Cargar imagen en el cliente
        image = vision.Image(content=content)

        # Detectar texto
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            texto_extraido = texts[0].description.strip()
            documento.texto_extraido = texto_extraido
        else:
            documento.texto_extraido = "(No se detectó texto legible)"

        documento.save()

        if response.error.message:
            raise Exception(response.error.message)

    except Exception as e:
        print(f"[Google OCR ERROR] {e}")
        documento.texto_extraido = f"(Error OCR: {e})"
        documento.save()
