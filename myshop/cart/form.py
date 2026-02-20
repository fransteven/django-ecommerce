from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    # this allows the user to select a quantity between 1 and 20
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
    )
    # this allows the user to override the quantity
    override = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput
    )
