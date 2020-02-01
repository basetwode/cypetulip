from django.conf.urls import url

from billing.views import GeneratePDF, HTMLPreview

__author__ = ''

urlpatterns = [
    url(r'^bill/(?P<order>[\S0-9_.-\\s\- ]*)$', GeneratePDF.as_view(), name='invoice_pdf'),
    url(r'^bill_pr/(?P<order>[\S0-9_.-\\s\- ]*)$', HTMLPreview.as_view(), name='invoice_pdf_preview')
]
