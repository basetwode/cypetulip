from django import forms
from django.forms import Form, CharField, ModelForm, Textarea
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.safestring import mark_safe

from shop.models import ProductAttributeType, IndividualOffer, OrderDetail, Address, Order, OrderItem
from utils.forms import SearchField, SearchableSelect


class ProductAttributeForm(ModelForm):
    class Meta:
        model = ProductAttributeType
        fields = []

    def __init__(self, product_attribute_types, *args, **kwargs):
        super().__init__(*args, **kwargs)
        interests = product_attribute_types  # kwargs.pop('product_attribute_types')
        request = args[0]
        for pa in product_attribute_types:
            field_name = '%s' % (pa.name,)
            self.fields[field_name] = CharField(required=False)
            try:
                self.initial[field_name] = request[pa.name]
            except (IndexError, MultiValueDictKeyError) as e:
                self.initial[field_name] = ''

    def clean(self):
        interests = set()
        i = 0
        field_name = '%s' % (i,)
        while self.cleaned_data.get(field_name):
            interest = self.cleaned_data[field_name]
            if interest in interests:
                self.add_error(field_name, 'Duplicate')
            else:
                interests.add(interest)
            i += 1
            field_name = 'interest_%s' % (i,)
        self.cleaned_data['interests'] = interests


class IndividualOfferForm(ModelForm):
    class Meta:
        model = IndividualOffer
        fields = '__all__'
        widgets = {
            'message': Textarea(attrs={'cols': 80, 'rows': 10}),
        }


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['company']
        required = ['company']

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


