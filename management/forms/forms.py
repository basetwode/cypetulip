from django.forms import ModelForm, CharField, Form, BooleanField, Textarea, forms, ModelMultipleChoiceField, \
    ModelChoiceField, FileField
from django.utils.translation import gettext_lazy as _

from shop.models.accounts import Company, Contact, Address
from shop.models.orders import OrderDetail, OrderItem
from shop.models.products import ProductSubItem, Product
from utils.forms import SearchField, SearchableSelect, SetPasswordForm, SearchableMultiSelect


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'is_public', 'price', 'special_price', 'price_on_request', 'tax', 'stock',
                  'max_items_per_order', 'description', 'details', 'assigned_sub_products', 'attributes',
                  'attribute_types']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['assigned_sub_products'].queryset = ProductSubItem.objects.filter(product=None)


class ContactUserForm(ModelForm):
    is_client_supervisor = BooleanField(required=False)

    class Meta:
        model = Contact
        fields = ['email', 'first_name', 'last_name', 'title', 'gender', 'telephone', 'language', 'billing_mail',
                  'is_client_supervisor']

    def clean(self):
        cleaned_data = super(ContactUserForm, self).clean()
        if Contact.objects.filter(username=cleaned_data.get("email")).exclude(id=self.instance.id).exists():
            raise forms.ValidationError(_('An user with the given email already exists'))
        return cleaned_data


class ContactUserIncludingPasswordForm(SetPasswordForm):
    is_client_supervisor = BooleanField(required=False)
    notify_customer = BooleanField(required=False)

    class Meta:
        model = Contact
        fields = ['email', 'first_name', 'last_name', 'title', 'gender', 'telephone', 'language',
                  'is_client_supervisor', 'notify_customer',
                  'new_password1',
                  'new_password2'
                  ]

    def clean(self):
        cleaned_data = super(ContactUserIncludingPasswordForm, self).clean()
        if Contact.objects.filter(username=cleaned_data.get("email")).exists():
            raise forms.ValidationError(_('An user with the given email already exists'))
        return cleaned_data


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
        model = OrderDetail
        fields = ['search', 'company']
        required = ['company']

        widgets = {
            'company': SearchableSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.filter(
            contact__groups__name__in=['client', 'client supervisor']).distinct()
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
        fields = ['search', 'product', 'count', 'price', 'price_wt', 'allowable', 'period_of_performance_start',
                  'period_of_performance_end']
        required = ['product', 'count']
        widgets = {
            'product': SearchableSelect(),
        }

    def __init__(self, order, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = True
        # self.fields['order_item'].queryset = OrderItem.objects.filter(order=order).exclude(id=self.instance.id)
        # self.fields['product'].queryset = Product.objects.all()


class PaymentProviderForm(Form):
    prepayment_enabled = BooleanField(label=_("Prepayment enabled"), required=False)
    prepayment_description = CharField(label=_("Prepayment description"), required=False, widget=Textarea)
    invoice_enabled = BooleanField(label=_('Invoice enabled'), required=False)
    invoice_description = CharField(label=_("Invoice description"), required=False, widget=Textarea)
    paypal_enabled = BooleanField(label=_('Paypal enabled'), required=False)
    paypal_use_sandbox = BooleanField(label=_('Paypal use sandbox'), required=False)
    paypal_description = CharField(label=_("Paypal description"), required=False, widget=Textarea)
    paypal_user = CharField(max_length=100, required=False, label=_('Paypal Client ID'))
    paypal_secret = CharField(max_length=100, required=False, label=_('Paypal Secret'))


class MergeAccountsForm(Form):
    search = CharField(max_length=20, help_text='Filter contacts', widget=SearchField(), required=False)
    contacts = ModelMultipleChoiceField(queryset=Contact.objects.all(), widget=SearchableMultiSelect)
    leading_contact = ModelChoiceField(queryset=Contact.objects.all())

    class Meta:
        fields = ['search', 'contacts']
        required = ['contacts']
        widgets = {
            'contacts': SearchableSelect(),
        }

    def __init__(self, contact, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = True
        self.initial['leading_contact'] = contact
        self.fields['contacts'].queryset = Contact.objects.all() \
            .exclude(id=contact.id) \
            .exclude(groups__name__in=['staff'])

    def clean(self):
        cleaned_data = super(MergeAccountsForm, self).clean()
        customer = Contact.objects.filter(username=cleaned_data.get("leading_contact").email)

        if customer.count() > 0 and customer[0].id != cleaned_data.get("leading_contact").id and customer.exists():
            raise forms.ValidationError(
                _('Can not merge into anonymous user, because there already is a registered user with this email. '
                  'Please select the existing user as the leading user.'))
        return cleaned_data


class ClearCacheForm(Form):
    clear_html_cache = BooleanField(label=_("Clear HTML Cache"), required=False)
    recompile_css_js = BooleanField(label=_("Recompile JS/CSS"), required=False)


class CustomerImportForm(Form):
    input_file = FileField(label=_("Import file"), required=False)
