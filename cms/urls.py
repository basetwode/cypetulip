from django.conf.urls import url
from cms.views import *

__author__ = ''

urlpatterns = [
    url(r'^admin/$', AdminView.as_view()),
    url(r'^theme.css$', CSSView.as_view()),
    url(r"^(?P<site>[a-zA-Z0-9_.-]+)/$", GenericView.as_view())
]