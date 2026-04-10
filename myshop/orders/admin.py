import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Order, OrderItem


def export_to_csv(modeladmin, request, queryset):
    # Accedemos a las opciones "meta" del modelo para obtener su nombre (verbose_name) y campos
    opts = modeladmin.model._meta

    # Indicamos que la respuesta HTTP debe descargarse como un archivo (attachment) y le damos un nombre
    content_disposition = f"attachment; filename={opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition

    # Creamos un escritor CSV que escribirá directamente en la respuesta HTTP
    writer = csv.writer(response)

    # Obtenemos los campos del modelo, excluyendo relaciones Muchos a Muchos y Uno a Muchos
    # ya que no se pueden representar fácilmente en una sola celda del archivo CSV
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]

    # Escribimos la cabecera (primera fila) usando los nombres legibles (verbose_name) de cada campo
    writer.writerow([field.verbose_name for field in fields])

    # Iteramos sobre los objetos que el usuario ha seleccionado para exportar
    for obj in queryset:
        data_row = []
        for field in fields:
            # Obtenemos el valor del campo respectivo en el objeto actual
            value = getattr(obj, field.name)

            # Si es un objeto de tipo fecha/hora, lo formateamos a una cadena DD/MM/YYYY
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)

        # Insertamos la fila completa con los datos de este objeto en el documento CSV
        writer.writerow(data_row)

    return response


export_to_csv.short_description = "Export to CSV"


def order_payment(obj):
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return ""


order_payment.short_description = "Stripe payment"


def order_detail(obj):
    return mark_safe(
        f'<a href="{reverse("admin:orders_order_change", args=[obj.id])}">View order</a>'
    )


order_detail.short_description = "Order"


def order_detail(obj):
    url = reverse("orders:admin_order_detail", args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def order_pdf(obj):
    url = reverse("orders:admin_order_pdf", args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')


order_pdf.short_description = "Invoice"


# Un Inline permite mostrar y editar modelos relacionados en la misma página del modelo principal
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "address",
        "postal_code",
        "city",
        "paid",
        order_payment,
        "created",
        "updated",
        order_detail,
        order_pdf,
    ]
    list_filter = ["paid", "created", "updated"]
    inlines = [OrderItemInline]
    actions = [export_to_csv]
