from cart.cart import Cart
from django.shortcuts import redirect, render

from .forms import OrderCreateForm
from .models import OrderItem
from .tasks import order_created


def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # form.save() crea una instancia del modelo Order con los datos del formulario
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    # Se pasa el objeto completo del carrito al modelo OrderItem
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )

            cart.clear()
            # launch the asynchronous task with Celery
            order_created.delay(order.id)
            # set the order in the session
            request.session["order_id"] = order.id
            # redirect for payment
            return redirect("payment:process")
    else:
        form = OrderCreateForm()
    return render(request, "orders/order/create.html", {"cart": cart, "form": form})
