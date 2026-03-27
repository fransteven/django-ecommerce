import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order


@csrf_exempt
def stripe_webhook(request):
    # Obtenemos el cuerpo de la petición, que contiene los datos del evento enviado por Stripe.
    payload = request.body

    # Obtenemos la firma digital de Stripe desde las cabeceras HTTP de la petición.
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

    # Inicializamos la variable event que almacenará el objeto de evento procesado.
    event = None

    try:
        # Utilizamos la librería de Stripe para verificar la firma y construir el evento.
        # Esto asegura que el evento realmente proviene de Stripe y no fue alterado usando nuestra clave secreta.
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Si los datos recibidos (payload) no son un JSON válido o están corruptos, devolvemos un error 400 (Bad Request).
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Si la firma no coincide (posible intento de fraude), devolvemos un error 400 (Bad Request).
        return HttpResponse(status=400)

    # Comprobamos si el tipo de evento recibido indica que el usuario completó exitosamente el pago en Stripe (checkout.session.completed).
    if event.type == "checkout.session.completed":
        # Extraemos el objeto que contiene la sesión de pago finalizada a partir de la información del evento.
        session = event.data.object

        # Validamos que el pago procesado fue mediante un pago único ("payment") y que el estado del mismo sea efectivamente "pagado" ("paid").
        if session.mode == "payment" and session.payment_status == "paid":
            try:
                # Buscamos en nuestra base de datos la orden a la que pertenece esta sesión,
                # utilizando el identificador (client_reference_id) que le facilitamos a Stripe al inicio de la sesión.
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                # Si por alguna razón la orden nunca existió o fue borrada de la base de datos, retornamos un HTTP 404 (No Encontrada).
                return HttpResponse(status=404)

            # Si todo está en regla, marcamos la orden como pagada (paid=True)
            order.paid = True

            # Almacena el id del pago hecho en Stripe
            order.stripe_id = session.payment_intent

            # Guardamos la orden con su nuevo estado en la base de datos
            order.save()

    # Si la validación es exitosa, respondemos a Stripe con un HTTP 200 (OK) indicando que recibimos el webhook correctamente.
    return HttpResponse(status=200)
