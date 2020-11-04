from django import forms
from django.forms import BooleanField
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from payment.models import Bill, CreditCard, PayPal


class LegalForm(forms.Form):
    gdpr = BooleanField(required=True,
                        label=mark_safe(_(
                            "I hereby consent that my data entered will be stored and processed for the purpose of fulfilling the contract. "
                            "The basis is Art. 6 Para. 1 lit. b GDPR. The duration of storage is set at 10 years in accordance with Section 257 (4) HGB."
                            "For more information, see our <a target='_blank' href='/cms/privacy-policy'>privacy policy</a>")))
    cancellation = BooleanField(required=True,
                                label=mark_safe(_(
                                    "I've read the <a target='_blank' href='/cms/cancellation-policy'>cancellation policy</a>")))

    general_business_terms = BooleanField(required=True,
                                          label=mark_safe(_(
                                              "I've read the <a target='_blank' href='/cms/gbt'>general business terms</a>")))


class PaymentForm(forms.ModelForm):
    pass

class CreditCardForm(PaymentForm):
    class Meta:
        model = CreditCard
        fields = '__all__'
        exclude = ['user', 'order', 'method']

    @staticmethod
    def _name():
        return 'Credit-card'


class BillForm(PaymentForm):
    class Meta:
        model = Bill
        fields = '__all__'
        exclude = ['user', 'order', 'method']

    @staticmethod
    def _name():
        return 'Bill'


class PayPalForm(PaymentForm):
    class Meta:
        model = PayPal
        fields = []

    @staticmethod
    def _name():
        return 'PayPal'


def PaymentFormFactory(class_name, form=None):
    subclasses = PaymentForm.__subclasses__()
    for subclass in subclasses:
        if subclass._name() == class_name:
            return subclass(form)


def get_all_payment_forms_as_dict():
    subclasses = PaymentForm.__subclasses__()
    result = {}
    for subclass in subclasses:
        result.setdefault(subclass._name(), subclass())
