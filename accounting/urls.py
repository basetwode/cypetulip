from django.conf.urls import url

__author__ = ''

from accounting.views import AccountingView, AccountingViewExportCSV, AccountingFullExport

app_name = "accounting"

urlpatterns = [
    url(r'^accounting/$', AccountingView.as_view(), name="index"),
    url(r'^accounting/export/csv/$', AccountingViewExportCSV.as_view(), name="export_csv"),
    url(r'^accounting/export/full/$', AccountingFullExport.as_view(), name="export"),
]
