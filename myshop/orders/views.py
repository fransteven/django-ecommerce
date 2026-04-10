from io import BytesIO

from cart.cart import Cart
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .forms import OrderCreateForm
from .models import Order, OrderItem
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


# Decorator to ensure that only staff members can access this view
# Valida que los campos is_active e is_staff sean True
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(
        request,
        "admin/orders/order/detail.html",
        {"order": order},
    )


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Header
    story.append(Paragraph("My Shop", styles["h1"]))
    story.append(Paragraph(f"Invoice no. {order.id}", styles["Normal"]))
    story.append(Paragraph(order.created.strftime("%b %d, %Y"), styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Bill to
    story.append(Paragraph("Bill to", styles["h3"]))
    story.append(Paragraph(f"{order.first_name} {order.last_name}", styles["Normal"]))
    story.append(Paragraph(order.email, styles["Normal"]))
    story.append(Paragraph(order.address, styles["Normal"]))
    story.append(Paragraph(f"{order.postal_code}, {order.city}", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Items table
    story.append(Paragraph("Items bought", styles["h3"]))
    table_data = [["Product", "Price", "Quantity", "Cost"]]
    for item in order.items.all():
        table_data.append([
            item.product.name,
            f"${item.price}",
            str(item.quantity),
            f"${item.get_cost()}",
        ])
    table_data.append(["", "", "Total", f"${order.get_total_cost()}"])

    table = Table(table_data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    # Payment status
    status_text = "✓ Paid" if order.paid else "Pending payment"
    story.append(Paragraph(status_text, styles["Normal"]))

    doc.build(story)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
    response.write(buffer.getvalue())
    return response
