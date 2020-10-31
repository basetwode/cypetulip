from django.forms import ModelForm, CharField

from shop.models import OrderDetail, Address, Order, OrderItem
from utils.forms import SearchField, SearchableSelect



class OrderForm(ModelForm):

    search = CharField(max_length=20, help_text='Filter companies', widget=SearchField(), required=False)

    class Meta:
        model = Order
        fields = ['search', 'company']
        required = ['company']

        widgets = {
            'company': SearchableSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = True


class OrderDetailForm(ModelForm):
    class Meta:
        model = OrderDetail
        fields = ['assigned_employee', 'state', 'contact', 'shipment_address', 'billing_address']
        required = ['state', 'contact', 'shipment_address', 'billing_address']

    def __init__(self, contacts, *args, **kwargs):
        super(OrderDetailForm, self).__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = True
        self.fields['contact'].queryset = contacts
        self.fields['shipment_address'].queryset = Address.objects.filter(contact__in=contacts)
        self.fields['billing_address'].queryset = Address.objects.filter(contact__in=contacts)
        if Address.objects.filter(contact__in=contacts).count() == 1:
            self.initial['shipment_address'] = Address.objects.get(contact__in=contacts)
            self.initial['billing_address'] = Address.objects.get(contact__in=contacts)
        if contacts.count() == 1:
            self.initial['contact'] = contacts.first()


class OrderItemForm(ModelForm):

    search = CharField(max_length=20, help_text='Filter products', widget=SearchField(), required=False)

    class Meta:
        model = OrderItem
        fields = ['search', 'product', 'count', 'price', 'price_wt']
        required = ['product', 'count']
        widgets = {
            'product': SearchableSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = True
