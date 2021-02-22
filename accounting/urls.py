from django.conf.urls import url

__author__ = ''

from accounting.views.main import AccountingView

app_name = "accounting"

urlpatterns = [
    url(r'^$', AccountingView.as_view(), name="index"),
]
