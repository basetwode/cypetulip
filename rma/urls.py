from django.urls import include, re_path

from rma.api import routes
from rma.views.main import RMAInitView

__author__ = ''

app_name = "rma"

urlpatterns = [
    re_path(r'^api/v1/', include(routes.router.urls)),
    re_path(r'^(?P<uuid>[\S0-9_.-\\s\-_ ]*)/init/$', RMAInitView.as_view(), name="rma_init"),
]
