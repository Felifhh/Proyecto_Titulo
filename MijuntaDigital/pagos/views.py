from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from transbank.webpay.webpay_plus.transaction import Transaction
from Reserva.models import Reserva, EspacioComunal
from Auditoria.utils import registrar_evento
from Usuarios.models import Vecino
from Certificados.models import Certificado
from pagos.models import Transaccion   
import requests




def notificar_n8n(evento, datos):
    webhook_url = "https://felifhhh.app.n8n.cloud/webhook/9a0798f9-34e0-4e76-b7c8-874c7f636a7a"  # URL definitiva
    try:
        requests.post(webhook_url, json={"evento": evento, **datos}, timeout=5)
        print(f" Evento '{evento}' enviado correctamente a n8n.")
    except Exception as e:
        print(f" Error enviando evento a n8n: {e}")

tx = Transaction()
tx.configure_for_testing()


def iniciar_pago(request):
    buy_order = "ORD-" + str(1234567)
    session_id = "SES-" + str(request.session.session_key)
    amount = 1000
    return_url = request.build_absolute_uri("/pagos/retorno/")

    response = tx.create(buy_order, session_id, amount, return_url)
    token = response["token"]
    url = response["url"]

    return render(request, "pagos/iniciar_pago.html", {"url": url, "token": token})


def retorno_pago(request):
    token = request.GET.get("token_ws")
    response = tx.commit(token)

    # Registrar transacción genérica
    Transaccion.objects.create(
        token=token,
        orden_compra=response.get("buy_order", ""),
        monto=response.get("amount", 0),
        estado=response.get("status", "Error").capitalize(),
        descripcion="Transacción de prueba o genérica"
    )

    return render(request, "pagos/resultado_pago.html", {"response": response})



def retorno_pago_certificado(request):
    token = request.GET.get("token_ws")

    if not token:
        messages.error(request, "Token de pago no recibido.")
        return redirect("home")

    tx = Transaction()
    tx.configure_for_testing()
    response = tx.commit(token)
    print(" Respuesta Transbank:", response)

    pago_data = request.session.get("certificado_pago")
    if not pago_data:
        messages.error(request, "No se encontró información del pago en sesión.")
        return redirect("home")

    status = response.get("status")
    monto = response.get("amount", 0)
    vecino = get_object_or_404(Vecino, pk=pago_data["vecino_id"])

    # Registrar transacción
    transaccion = Transaccion.objects.create(
        id_vecino=vecino,
        token=token,
        orden_compra=response.get("buy_order", ""),
        monto=monto,
        estado=response.get("status", "Error").capitalize(),  # p.ej. Authorized / Failed
        descripcion=f"Pago de certificado tipo {pago_data['tipo']}"
    )

    if status == "AUTHORIZED":
        certificado = Certificado.objects.create(
            id_vecino=vecino,
            tipo=pago_data["tipo"],
            estado="Pendiente"
        )

        # Notificar a n8n para que genere y envíe la boleta del certificado
        notificar_n8n("certificado_pagado", {
            "id_vecino": vecino.id_vecino,
            "nombre": vecino.nombre,
            "correo": vecino.correo,
            "run": vecino.run,

            "tipo_certificado": certificado.tipo,
            "estado_certificado": certificado.estado,

            "orden_compra": transaccion.orden_compra,
            "token": transaccion.token,
            "monto_total": int(transaccion.monto or 0),
            "estado": transaccion.estado,
            "descripcion": transaccion.descripcion,
            "fecha_transaccion": (
                timezone.localtime(transaccion.fecha).strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(transaccion, "fecha") and transaccion.fecha
                else timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
            ),
        })

        registrar_evento(
            request,
            f"Pago certificado '{certificado.tipo}' registrado (#{certificado.id_certificado})",
            "Pago autorizado"
        )

        request.session.pop("certificado_pago", None)
        messages.success(request, "Pago realizado con éxito. Tu solicitud fue enviada al directorio.")
        return render(request, "pagos/resultado_pago.html", {"response": response, "certificado": certificado})

    else:
        registrar_evento(
            request,
            f"Pago no autorizado para certificado tipo '{pago_data.get('tipo')}'",
            f"Estado: {status}"
        )

        messages.error(request, f"Pago no autorizado. Estado: {status}")
        return render(request, "pagos/resultado_pago.html", {"response": response})



def retorno_pago_reserva(request):
    token = request.GET.get("token_ws")
    tx = Transaction()
    tx.configure_for_testing()
    response = tx.commit(token)
    pago_data = request.session.get("reserva_pago")

    if not pago_data:
        registrar_evento(request, "Error en retorno de pago Webpay: sin datos de reserva", "Error")
        messages.error(request, "No se encontró información de la reserva en sesión.")
        return redirect("home")

    status = response.get("status")
    monto = response.get("amount", 0)
    vecino = get_object_or_404(Vecino, pk=pago_data["vecino_id"])
    espacio = get_object_or_404(EspacioComunal, pk=pago_data["espacio_id"])

    # Registrar transacción
    transaccion = Transaccion.objects.create(
        id_vecino=vecino,
        token=token,
        orden_compra=response.get("buy_order", ""),
        monto=monto,
        estado=response.get("status", "Error").capitalize(),
        descripcion=f"Pago por reserva del espacio {espacio.nombre}"
    )

    # Si el pago fue exitoso
    if status == "AUTHORIZED":
        reserva = Reserva.objects.create(
            id_vecino=vecino,
            id_espacio=espacio,
            fecha=pago_data["fecha"],
            hora_inicio=pago_data["hora_inicio"],
            hora_fin=pago_data["hora_fin"],
            estado="Activa",
            total=pago_data["total"],
        )

        # Enviar todos los datos al n8n (para generar boleta y correo)
        notificar_n8n("reserva_pagada", {
            "nombre": vecino.nombre,
            "correo": vecino.correo,
            "run": vecino.run,
            "id_vecino": vecino.id_vecino,
            "id_espacio": espacio.id_espacio,
            "nombre_espacio": espacio.nombre,
            "fecha": str(reserva.fecha),
            "hora_inicio": str(reserva.hora_inicio),
            "hora_fin": str(reserva.hora_fin),
            "monto_total": int(reserva.total),
            "reserva_id": reserva.id_reserva,
            "orden_compra": transaccion.orden_compra,
            "token": transaccion.token,
            "estado": transaccion.estado,
            "descripcion": transaccion.descripcion,
            "fecha_transaccion": (
                timezone.localtime(transaccion.fecha).strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(transaccion, "fecha") and transaccion.fecha
                else timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
            ),
        })

        registrar_evento(request, f"Reserva pagada correctamente y enviada al n8n (#{reserva.id_reserva})", "Pago autorizado")
        request.session.pop("reserva_pago", None)
        messages.success(request, f"Reserva pagada correctamente. Información enviada al sistema de boletas (n8n).")
        return render(request, "pagos/resultado_pago.html", {"response": response, "reserva": reserva})

    # Si el pago fue rechazado
    else:
        registrar_evento(request, f"Pago rechazado para reserva en '{pago_data['espacio_id']}'", f"Estado: {status}")
        messages.error(request, "El pago fue rechazado o cancelado.")
        return render(request, "pagos/resultado_pago.html", {"response": response})
