from django.urls import re_path

from billing.views.main import GeneratePDF, HTMLPreview

__author__ = ''
app_name = 'billing'

urlpatterns = [
    re_path(r'^bill/(?P<order>[\S0-9_.-\\s\- ]*)$', GeneratePDF.as_view(), name='invoice_pdf'),
    re_path(r'^bill_pr/(?P<order>[\S0-9_.-\\s\- ]*)$', HTMLPreview.as_view(), name='invoice_pdf_preview')
]
