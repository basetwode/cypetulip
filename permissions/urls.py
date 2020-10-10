from django.conf.urls import url

from permissions.views import PermissionDeniedView

__author__ = ''

urlpatterns = [
    url(r'^403/$', PermissionDeniedView.as_view(), name='permission_denied'),
]
