from django.conf.urls import url

from shipping.views import CreateOnlineShipment, CreatePackageShipment, ShowOnlineShipment, ShowPackageShipment, \
    DeleteShipment

__author__ = ''


app_name = "shipping"

urlpatterns = [
    url(r'^onlineshipment/create/(?P<order>[a-zA-Z0-9\\s\-_ ]+)$', CreateOnlineShipment.as_view(),
        name='onlineshipment_create'),
    url(r'^packageshipment/create/(?P<order>[a-zA-Z0-9\\s\-_ ]+)$', CreatePackageShipment.as_view(),
        name='packageshipment_create'),
    url(r'^onlineshipment/(?P<id>[0-9]+)$', ShowOnlineShipment.as_view(), name='onlineshipment_show'),
    url(r'^packageshipment/(?P<id>[0-9]+)$', ShowPackageShipment.as_view(), name='packageshipment_show'),
    url(r'^shipment/(?P<order>[a-zA-Z0-9\\s\-_ ]+)/delete/(?P<url_param>[0-9]+)$', DeleteShipment.as_view(),
        name='shipment_delete')
]
