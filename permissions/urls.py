from django.urls import re_path

from permissions.views.main import PermissionDeniedView

app_name = 'permissions'

urlpatterns = [
    re_path(r'^403/$', PermissionDeniedView.as_view(), name='permission_denied'),
]
