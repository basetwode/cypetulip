from django.conf.urls import url

__author__ = ''

from accounting.views import AccountingView

app_name = "accounting"

urlpatterns = [
    url(r'^accounting/$', AccountingView.as_view(), name="index"),
]
