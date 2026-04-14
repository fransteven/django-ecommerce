import logging
from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from orders.models import Order
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

logger = logging.getLogger(__name__)


@shared_task
def payment_completed(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully paid.
    """
    order = Order.objects.get(id=order_id)
    # create invoice e-mail
    subject = f"My Shop - Invoice no. {order.id}"
    message = "Please, find attached the invoice for your recent purchase."
    email = EmailMessage(
        subject, message, settings.DEFAULT_FROM_EMAIL, [order.email]
    )
    # generate PDF
    out = BytesIO()
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
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
    status_text = "PAID" if order.paid else "Pending payment"
    story.append(Paragraph(status_text, styles["Normal"]))

    doc.build(story)

    pdf_bytes = out.getvalue()
    logger.info("PDF generated for order %s — size: %d bytes", order.id, len(pdf_bytes))

    if not pdf_bytes:
        logger.error("PDF generation produced empty output for order %s", order.id)
        raise ValueError(f"Empty PDF for order {order.id}")

    # attach PDF file
    email.attach(f"order_{order.id}.pdf", pdf_bytes, "application/pdf")
    # send e-mail
    email.send()
