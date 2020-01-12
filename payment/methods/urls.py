from django.conf.urls import include, url

from payment.methods.bill import urls as bill_urls

app_name = 'methods'
urlpatterns = [
    url(r'^bill/', include(bill_urls, namespace='bill')),
    # url(r'paypal/', include(paypal_urls)),
    # url(r'sofort/', include(sofort_urls)),
]
