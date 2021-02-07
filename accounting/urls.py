from django.conf.urls import url

__author__ = ''

from accounting.views.views import AccountingView, AccountingViewExportCSV, AccountingFullExport

app_name = "accounting"

urlpatterns = [
    url(r'^$', AccountingView.as_view(), name="index"),
    url(r'^export/csv/$', AccountingViewExportCSV.as_view(), name="export_csv"),
    url(r'^export/full/$', AccountingFullExport.as_view(), name="export"),
]
