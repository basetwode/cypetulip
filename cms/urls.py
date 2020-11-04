from django.conf.urls import url

from cms.views import *

__author__ = ''

app_name = 'cms'

urlpatterns = [
    url(r'^admin/$', AdminView.as_view()),
    url(r'^permissions-denied/$', PermissionDeniedView.as_view(), name='permissions_denied'),
    url(r'^theme.css$', CSSView.as_view()),
    url(r"^(?P<site>[a-zA-Z0-9_.-]+)/$", GenericView.as_view(), name="generic_cms_page")
]
