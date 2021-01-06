from django.conf.urls import url

from rma.views import RMAInitView

__author__ = ''


app_name = "rma"

urlpatterns = [
    url(r'^(?P<order_hash>[\S0-9_.-\\s\-_ ]*)/init/$', RMAInitView.as_view(), name="rma_init"),
]
