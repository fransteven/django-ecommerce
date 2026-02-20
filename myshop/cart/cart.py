from decimal import Decimal
from typing import Iterator, Optional

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest
from shop.models import Product


class Cart:
    def __init__(self, request: HttpRequest) -> None:
        """
        Initialize the cart.
        """
        self.session: SessionBase = request.session
        cart: Optional[dict] = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart: dict = cart

    def add(
        self, product: Product, quantity: int = 1, override_quantity: bool = False
    ) -> None:
        """
        Add a product to the cart or update its quantity.
        """
        product_id: str = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def save(self) -> None:
        """
        Mark the session as "modified" to make sure it gets saved.
        """
        self.session.modified = True

    def remove(self, product: Product) -> None:
        """
        Remove a product from the cart.
        """
        product_id: str = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self) -> Iterator[dict]:
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart: dict = self.cart.copy()
        for product in products:
            cart[str(product.id)]["product"] = product
        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            # yield allows that Cart object to be used as an iterator
            yield item

    def __len__(self) -> int:
        """
        Return the number of items in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        """
        Return the total price of all items in the cart.
        """
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    def clear(self) -> None:
        """
        Remove all items from the cart.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
