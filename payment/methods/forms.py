from django import forms

from payment.models import Bill, CreditCard


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
