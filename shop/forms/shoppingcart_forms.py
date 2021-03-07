from django.forms import ModelForm
from requests.compat import basestring

from shop.models.accounts import Address, Contact
from shop.models.orders import OrderItem, FileOrderItem, SelectOrderItem, CheckBoxOrderItem, NumberOrderItem

__author__ = 'Anselm'


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ('name', 'street', 'number', 'zipcode', 'city')


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ('first_name', 'last_name', 'gender', 'telephone', 'email')


class OrderItemForm(ModelForm):
    class Meta:
        model = OrderItem
        fields = []