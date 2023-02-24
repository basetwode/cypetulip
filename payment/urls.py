from django.urls import include, re_path

from payment.api import routes
from payment.views.main import (
    PaymentCreateView, PaymentConfirmView, PaymentSubmitView)
from payment.views.paypal import PaypalPaymentConfirmationView, PaypalSubmitView

__author__ = ''
app_name = 'payment'

urlpatterns = [
    re_path(r'^api/v1/', include(routes.router.urls)),

    re_path(r"^(?P<uuid>[\S0-9_.-\\s\-_ ]*)/paypal/$",
            PaypalPaymentConfirmationView.as_view(), name="paypal"),
    re_path(r"^(?P<uuid>[\S0-9_.-\\s\-_ ]*)/paypal/submit",
            PaypalSubmitView.as_view(), name="paypal_submit"),

    re_path(r"^(?P<uuid>[\S0-9_.-\\s\-_ ]*)/bill/$",
            PaymentConfirmView.as_view(), name="bill"),
    re_path(r"^(?P<uuid>[\S0-9_.-\\s\-_ ]*)/bill/submit/$",
            PaymentSubmitView.as_view(), name="bill_submit"),

    re_path(r"^(?P<uuid>[\S0-9_.-\\s\-_ ]*)/prepayment/$",
            PaymentConfirmView.as_view(), name="prepayment"),
    re_path(r"^(?P<uuid>[\S0-9_.-\\s\-_ ]*)/prepayment/submit/$",
            PaymentSubmitView.as_view(), name="prepayment_submit"),

    re_path(r"^(?P<uuid>[\S0-9_.-\\s\-_ ]*)/$",
            PaymentCreateView.as_view(), name="payment"),


]
