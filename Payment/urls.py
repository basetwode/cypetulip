from django.conf.urls import url, include
from html5lib.treeadapters.sax import namespace

from Payment.methods import urls as method_urls


from Payment.views import PaymentView, PaymentCreationView, PaymentConfirmationView

__author__ = ''


urlpatterns = [
    url(r"^(?P<order>[a-zA-Z0-9\\s\- ]+)/$", PaymentView.as_view(),name="payment"),
    url(r"^(?P<order>[a-zA-Z0-9\\s\- ]+)/create/$",
       PaymentCreationView.as_view(), name="payment_create"),
    url(r"^(?P<order>[a-zA-Z0-9\\s\- ]+)/confirm/$",
       PaymentConfirmationView.as_view(),name="blabla"),
    url(r"^(?P<order>[a-zA-Z0-9\\s\- ]+)/", include(method_urls,namespace="payment"),name="bla"),
   url(r"confirm/^(?P<order>[\S0-9_.-\\s\- ]+)/(?P<payment_method>[0-9]+)/(?P<payment_hash>[0-9]+)$",
      PaymentConfirmationView.as_view())
]
