from django.conf.urls import url

__author__ = ''

from accounting.views import AccountingView

urlpatterns = [
    url(r'^accounting/$', AccountingView.as_view(), name="accounting"),
]
