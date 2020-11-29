from django.contrib.auth.models import User
from django.forms import ModelForm, CharField, Form, BooleanField, Textarea, forms
from django.utils.translation import ugettext_lazy as _

from shop.models import OrderDetail, Address, Order, OrderItem, Product, ProductSubItem, Contact
from utils.forms import SearchField, SearchableSelect, SetPasswordForm


class ProductForm(ModelForm):

    class Meta:
        model = Product
        fields = ['name','category', 'is_public','price', 'special_price', 'price_on_request', 'tax','stock',
                  'max_items_per_order', 'description', 'details',
                  'product_picture',   'assigned_sub_products', 'attributes']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['assigned_sub_products'].queryset = ProductSubItem.objects.filter(product=None)


class ContactUserForm(ModelForm):

    is_client_supervisor = BooleanField(required=False)

    class Meta:
        model = Contact
        fields = ['email','first_name','last_name','title','gender','telephone','language',
                  'is_client_supervisor']

    def clean(self):
        cleaned_data = super(ContactUserForm, self).clean()
        if Contact.objects.filter(username=cleaned_data.get("email")).exists():
            raise forms.ValidationError(_('An user with the given email already exists'))
        return cleaned_data


class ContactUserIncludingPasswordForm(SetPasswordForm):

    is_client_supervisor = BooleanField(required=False)
    notify_customer = BooleanField(required=False)

    class Meta:
        model = Contact
        fields = ['email','first_name','last_name','title','gender','telephone','language',
                  'is_client_supervisor', 'notify_customer',
                  'new_password1',
                  'new_password2'
                  ]


class ContactUserUpdatePasswordForm(SetPasswordForm):

    notify_customer = BooleanField(required=False)

    class Meta:
        model = Contact
        fields = [
                  'new_password1',
                  'new_password2'
                  ]


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
        fields = ['search', 'product', 'count', 'price', 'price_wt','order_item']
        required = ['product', 'count']
        widgets = {
            'product': SearchableSelect(),
        }

    def __init__(self, order, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = True
        self.fields['order_item'].queryset = OrderItem.objects.filter(order=order).exclude(id=self.instance.id)


class PaymentProviderForm(Form):
    prepayment_enabled = BooleanField(label=_("Prepayment enabled"), required=False)
    prepayment_description = CharField(label=_("Prepayment description"), required=False, widget=Textarea)
    invoice_enabled = BooleanField(label=_('Invoice enabled'), required=False)
    invoice_description = CharField(label=_("Invoice description"), required=False, widget=Textarea)
    paypal_enabled = BooleanField(label=_('Paypal enabled'), required=False)
    paypal_description = CharField(label=_("Paypal description"), required=False, widget=Textarea)
    paypal_user = CharField(max_length=100, required=False,label=_('Paypal Client ID'))
    paypal_secret = CharField(max_length=100, required=False, label=_('Paypal Secret'))