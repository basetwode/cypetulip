from django.conf.urls import url

from payment.views.paypal import PaypalPaymentConfirmationView, PaypalSubmitView
from payment.views.main import (
    PaymentCreateView, PaymentConfirmView, PaymentSubmitView)

__author__ = ''
app_name = 'payment'

urlpatterns = [

    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/paypal/$",
        PaypalPaymentConfirmationView.as_view(), name="paypal"),
    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/paypal/submit",
        PaypalSubmitView.as_view(), name="paypal_submit"),

    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/bill/$",
        PaymentConfirmView.as_view(), name="bill"),
    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/bill/submit/$",
        PaymentSubmitView.as_view(), name="bill_submit"),

    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/prepayment/$",
        PaymentConfirmView.as_view(), name="prepayment"),
    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/prepayment/submit/$",
        PaymentSubmitView.as_view(), name="prepayment_submit"),

    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/$",
        PaymentCreateView.as_view(), name="payment"),


]
