from django.conf.urls import url, include
from html5lib.treeadapters.sax import namespace

from methods import urls as method_urls
from views import *
from methods import bill
__author__ = ''


urlpatterns = [
    url(r"^(?P<order>[a-zA-Z0-9\\s\- ]+)/$", PaymentView.as_view()),
    url(r"^(?P<order>[a-zA-Z0-9\\s\- ]+)/create/$",
       PaymentCreationView.as_view()),
    url(r"^(?P<order>[a-zA-Z0-9\\s\- ]+)/confirm/$",
       PaymentConfirmationView.as_view(),name="blabla"),
    url(r"^(?P<order>[a-zA-Z0-9\\s\- ]+)/", include(method_urls,namespace="payment"),name="bla"),

]
#    url(r"confirm/^(?P<order>[\S0-9_.-\\s\- ]+)/(?P<payment_method>[0-9]+)/(?P<payment_hash>[0-9]+)$",
#       PaymentConfirmationView.as_view())