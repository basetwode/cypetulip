from django.urls import include, re_path

from shipping.api import routes
from shipping.views.main import CreateOnlineShipment, CreatePackageShipment, ShowOnlineShipment, ShowPackageShipment, \
    DeleteShipment

__author__ = ''


app_name = "shipping"

urlpatterns = [
    re_path(r'^api/v1/', include(routes.router.urls)),
    re_path(r'^onlineshipment/create/(?P<order>[a-zA-Z0-9\\s\-_ ]+)$', CreateOnlineShipment.as_view(),
            name='onlineshipment_create'),
    re_path(r'^packageshipment/create/(?P<order>[a-zA-Z0-9\\s\-_ ]+)$', CreatePackageShipment.as_view(),
            name='packageshipment_create'),
    re_path(r'^onlineshipment/(?P<id>[0-9]+)$', ShowOnlineShipment.as_view(), name='onlineshipment_show'),
    re_path(r'^packageshipment/(?P<id>[0-9]+)$', ShowPackageShipment.as_view(), name='packageshipment_show'),
    re_path(r'^shipment/(?P<order>[a-zA-Z0-9\\s\-_ ]+)/delete/(?P<url_param>[0-9]+)$', DeleteShipment.as_view(),
            name='shipment_delete')
]
