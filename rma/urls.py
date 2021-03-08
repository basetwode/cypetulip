from django.conf.urls import url
from django.urls import include

from rma.api import routes
from rma.views.main import RMAInitView

__author__ = ''


app_name = "rma"

urlpatterns = [
    url(r'^api/v1/', include(routes.router.urls)),
    url(r'^(?P<uuid>[\S0-9_.-\\s\-_ ]*)/init/$', RMAInitView.as_view(), name="rma_init"),
]
