from django.conf.urls import url

from payment.methods.bill.views import BillConfirmView, BillSubmitView
from payment.methods.paypal.views import PaypalPaymentConfirmationView, PaypalSubmitView
from payment.methods.prepayment.views import PrepaymentConfirmView, PrepaymentSubmitView
from payment.views import (PaymentConfirmationView, PaymentCreationView,
                           PaymentView)

__author__ = ''
app_name = 'payment'

urlpatterns = [
    # url(r"^(?P<order>[\S0-9_.-\\s\- ]*)/", include(method_urls, namespace='methods')),


    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/paypal/$",
        PaypalPaymentConfirmationView.as_view(), name="paypal"),
    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/paypal/submit",
        PaypalSubmitView.as_view(), name="paypal_submit"),

    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/bill/$",
        BillConfirmView.as_view(), name="bill"),
    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/bill/submit/$",
        BillSubmitView.as_view(), name="bill_submit"),

    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/prepayment/$",
        PrepaymentConfirmView.as_view(), name="prepayment"),
    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/prepayment/submit/$",
        PrepaymentSubmitView.as_view(), name="prepayment_submit"),

    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/create/$",
        PaymentCreationView.as_view(), name="payment_create"),
    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/$",
        PaymentView.as_view(), name="payment"),

    url(r"^(?P<order>[\S0-9_.-\\s\-_ ]*)/confirm/$",
        PaymentConfirmationView.as_view(), name="payment_confirm"),
    url(r"confirm/^(?P<order>[\S0-9_.-\\s\-_ ]*)/(?P<payment_method>[0-9]+)/(?P<payment_hash>[0-9]+)$",
        PaymentConfirmationView.as_view()),

]
