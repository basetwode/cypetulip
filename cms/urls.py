from django.conf.urls import url

from cms.views import *

__author__ = ''

app_name = 'cms'

urlpatterns = [
    url(r'^admin/$', AdminView.as_view()),
    url(r'^permissions-denied/$', PermissionDeniedView.as_view(), name='permissions_denied'),
    url(r'^theme.css$', CSSView.as_view()),
    url(r"contact/$", ContactView.as_view(), name="contact"),
    url(r"legal/$", LegalView.as_view(), name="legal"),
    url(r"general-business-terms/$", GBTView.as_view(), name="gbt"),
    url(r"cancellation-policy/$", CancellationPolicyView.as_view(), name="cancellation-policy"),
    url(r"privacy-policy/$", PrivacyPolicyView.as_view(), name="privacy-policy"),
    url(r"^(?P<site>[a-zA-Z0-9_.-]+)/$", GenericView.as_view(), name="generic_cms_page")
]
