from django.conf.urls import url, include
from bill import urls as bill_urls
from paypal import urls as paypal_urls
from sofort import urls as sofort_urls

urlpatterns = [
    url(r'bill/', include(bill_urls)),
    #url(r'paypal/', include(paypal_urls)),
    #url(r'sofort/', include(sofort_urls)),
]