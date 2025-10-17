import qrcode
import os
from django.conf import settings
from datetime import datetime

def generar_folio():
    fecha = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"RES-{fecha}"

def generar_qr(folio):
    qr_dir = os.path.join(settings.MEDIA_ROOT, "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)
    file_path = os.path.join(qr_dir, f"{folio}.png")
    qr_img = qrcode.make(f"Certificado: {folio}")
    qr_img.save(file_path)
    return f"qr_codes/{folio}.png"
