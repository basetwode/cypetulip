from django.urls import re_path

__author__ = ''

from accounting.views.main import AccountingView

app_name = "accounting"

urlpatterns = [
    re_path(r'^$', AccountingView.as_view(), name="index"),
]
