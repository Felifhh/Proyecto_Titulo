from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import pandas as pd
from .ia_engine import generar_analisis_ia
from pagos.models import Transaccion
from Reserva.models import Reserva
from Certificados.models import Certificado

def generar_reporte_completo():
    # Buffers
    pdf_buffer = BytesIO()
    excel_buffer = BytesIO()

    # Obtener datos reales
    total_monto = Transaccion.objects.filter(estado="Authorized").aggregate(sum_monto=pd.Sum("monto"))["sum_monto"] or 0
    reservas_count = Reserva.objects.count()
    certificados_count = Certificado.objects.count()

    # IA
    analisis_ia = generar_analisis_ia(reservas_count, certificados_count, total_monto)

    # ===== PDF =====
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    story = []

    story.append(Paragraph("<b>Reporte Semanal de Gestión</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>Monto Recaudado:</b> ${total_monto:,}", styles["Normal"]))
    story.append(Paragraph(f"<b>Reservas realizadas:</b> {reservas_count}", styles["Normal"]))
    story.append(Paragraph(f"<b>Certificados emitidos:</b> {certificados_count}", styles["Normal"]))

    story.append(Spacer(1, 20))
    story.append(Paragraph(analisis_ia, styles["Normal"]))

    doc.build(story)
    pdf_bytes = pdf_buffer.getvalue()

    # ===== EXCEL =====
    df = pd.DataFrame({
        "métrica": ["Monto Recaudado", "Reservas", "Certificados"],
        "valor": [total_monto, reservas_count, certificados_count]
    })

    df.to_excel(excel_buffer, index=False)
    excel_bytes = excel_buffer.getvalue()

    return pdf_bytes, excel_bytes
