from django.conf.urls import url
from django.views.decorators.cache import cache_page

from cms.views import *

__author__ = ''

app_name = 'cms'

urlpatterns = [
    url(r'^admin/$', AdminView.as_view()),
    url(r'^permissions-denied/$', PermissionDeniedView.as_view(), name='permissions_denied'),
    url(r'^theme.css$', CSSView.as_view()),
    url(r"contact/$", ContactView.as_view(), name="contact"),
    url(r"legal/$", cache_page(60*60)(LegalView.as_view()), name="legal"),
    url(r"general-business-terms/$", cache_page(60*60)(GBTView.as_view()), name="gbt"),
    url(r"cancellation-policy/$", cache_page(60*60)(CancellationPolicyView.as_view()), name="cancellation-policy"),
    url(r"privacy-policy/$", cache_page(60*60)(PrivacyPolicyView.as_view()), name="privacy-policy"),
    url(r"^(?P<site>[a-zA-Z0-9_.-]+)/$", cache_page(60*60)(GenericView.as_view()), name="generic_cms_page")
]
