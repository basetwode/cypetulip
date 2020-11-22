from django.conf.urls import url

from permissions.views import PermissionDeniedView

app_name = 'permissions'

urlpatterns = [
    url(r'^403/$', PermissionDeniedView.as_view(), name='permission_denied'),
]
