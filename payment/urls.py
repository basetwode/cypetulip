from django.conf.urls import include, url

from payment.methods import urls as method_urls
from payment.views import (PaymentConfirmationView, PaymentCreationView,
                           PaymentView)

__author__ = ''
app_name = 'payment'

urlpatterns = [
    url(r"^(?P<order>[\S0-9_.-\\s\- ]*)/",
        include(method_urls, namespace='methods')),
    url(r"^(?P<order>[\S0-9_.-\\s\- ]*)/create/$",
        PaymentCreationView.as_view(), name="payment_create"),
    url(r"^(?P<order>[\S0-9_.-\\s\- ]*)/$",
        PaymentView.as_view(), name="payment"),

    url(r"^(?P<order>[\S0-9_.-\\s\- ]*)/confirm/$",
        PaymentConfirmationView.as_view(), name="payment_confirm"),
    url(r"confirm/^(?P<order>[\S0-9_.-\\s\- ]*)/(?P<payment_method>[0-9]+)/(?P<payment_hash>[0-9]+)$",
        PaymentConfirmationView.as_view()),
]
