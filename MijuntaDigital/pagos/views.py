from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from transbank.webpay.webpay_plus.transaction import Transaction
from Reserva.models import Reserva, EspacioComunal

from Usuarios.models import Vecino
import requests


def notificar_n8n(evento, datos):
    webhook_url = "https://felifhh.app.n8n.cloud/webhook/evento-app"  # URL definitiva
    try:
        requests.post(webhook_url, json={"evento": evento, **datos}, timeout=5)
        print(f" Evento '{evento}' enviado correctamente a n8n.")
    except Exception as e:
        print(f" Error enviando evento a n8n: {e}")

#  Configurar entorno de pruebas instanciando Transaction
tx = Transaction()
tx.configure_for_testing()


def iniciar_pago(request):
    buy_order = "ORD-" + str(123456)
    session_id = "SES-" + str(request.session.session_key)
    amount = 1000
    return_url = request.build_absolute_uri("/pagos/retorno/")

    #  Llamar al método create usando la instancia configurada
    response = tx.create(buy_order, session_id, amount, return_url)
    token = response["token"]
    url = response["url"]

    return render(
        request, "pagos/iniciar_pago.html", {"url": url, "token": token}
    )


def retorno_pago(request):
    token = request.GET.get("token_ws")
    response = tx.commit(token)
    return render(request, "pagos/resultado_pago.html", {"response": response})

from Certificados.models import Certificado

def retorno_pago_certificado(request):
    token = request.GET.get("token_ws")

    if not token:
        messages.error(request, "Token de pago no recibido.")
        return redirect("home")

    # Crear transacción y confirmar pago
    tx = Transaction()
    tx.configure_for_testing()
    response = tx.commit(token)  # <-- Devuelve dict, no objeto

    # Ver el contenido de la respuesta en consola
    print(" Respuesta Transbank:", response)

    pago_data = request.session.get("certificado_pago")
    if not pago_data:
        messages.error(request, "No se encontró información del pago en sesión.")
        return redirect("home")

    #  Verificar si el pago fue autorizado
    status = response.get("status")
    if status == "AUTHORIZED":
        vecino = get_object_or_404(Vecino, pk=pago_data["vecino_id"])

        # Crear certificado solo si el pago fue exitoso
        certificado = Certificado.objects.create(
            id_vecino=vecino,
            tipo=pago_data["tipo"],
            estado="Pendiente",
            fecha_emision=None,
            folio=None,
            qr_code=None,
            firma_digital=None,
        )

        # Limpiar sesión temporal
        request.session.pop("certificado_pago", None)

        messages.success(request, "Pago realizado con éxito. Tu solicitud fue enviada al directorio.")

        return render(request, "pagos/resultado_pago.html", {
            "response": response,
            "certificado": certificado
        })

    # Si el pago fue rechazado o falló
    else:
        messages.error(request, f"Pago no autorizado. Estado: {status}")
        return render(request, "pagos/resultado_pago.html", {"response": response})
    


def retorno_pago_reserva(request):
    token = request.GET.get("token_ws")
    tx = Transaction()
    tx.configure_for_testing()
    response = tx.commit(token)
    pago_data = request.session.get("reserva_pago")

    if not pago_data:
        messages.error(request, "No se encontró información de la reserva en sesión.")
        return redirect("home")

    if response.get("status") == "AUTHORIZED":
        vecino = get_object_or_404(Vecino, pk=pago_data["vecino_id"])
        espacio = get_object_or_404(EspacioComunal, pk=pago_data["espacio_id"])

        # Crear la reserva
        reserva = Reserva.objects.create(
            id_vecino=vecino,
            id_espacio=espacio,
            fecha=pago_data["fecha"],
            hora_inicio=pago_data["hora_inicio"],
            hora_fin=pago_data["hora_fin"],
            estado="Activa",
            total=pago_data["total"],
        )

        # Notificar al n8n (como en tu función original)
        notificar_n8n("reserva_activa", {
            "nombre": vecino.nombre,
            "correo": vecino.correo,
            "run": vecino.run,
            "id_espacio": espacio.id_espacio,
            "nombre_espacio": espacio.nombre,
            "fecha": reserva.fecha,
            "hora_inicio": reserva.hora_inicio,
            "hora_fin": reserva.hora_fin,
            "monto_total": reserva.total,
            "reserva_id": reserva.id_reserva,
        })

        # Limpia la sesión
        request.session.pop("reserva_pago", None)

        messages.success(request, f" Reserva pagada correctamente. Monto total: ${reserva.total:,}.")
        return render(request, "pagos/resultado_pago.html", {
            "response": response,
            "reserva": reserva,
        })

    else:
        messages.error(request, " El pago fue rechazado o cancelado. No se generó la reserva.")
        return render(request, "pagos/resultado_pago.html", {"response": response})
