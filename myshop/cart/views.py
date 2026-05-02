from coupons.forms import CouponApplyForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from shop.models import Product

from .cart import Cart
from .form import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    # create a form instance and validate the posted data
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        # cart.add store the product and quantity in the session
        cart.add(
            product=product, quantity=cd["quantity"], override_quantity=cd["override"]
        )
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    # cart.remove remove the product from the session
    cart.remove(product)

    return redirect("cart:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    coupon_apply_form = CouponApplyForm()
    return render(
        request,
        "cart/detail.html",
        {
            "cart": cart,
            "coupon_apply_form": coupon_apply_form,
        },
    )
