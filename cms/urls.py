from django.conf.urls import url
from django.views.decorators.cache import cache_page

from cms.views.views import *
from home.settings import CACHE_MIDDLEWARE_SECONDS

__author__ = ''

app_name = 'cms'

urlpatterns = [
    url(r'^admin/$', AdminView.as_view()),
    url(r'^permissions-denied/$', PermissionDeniedView.as_view(), name='permissions_denied'),
    url(r'^css-setting/(?P<css_settings_id>[a-zA-Z0-9_.-]*)$', CSSSettingsView.as_view(), name='css-settings'),
    url(r"contact/$", ContactView.as_view(), name="contact"),
    url(r"legal/$", cache_page(CACHE_MIDDLEWARE_SECONDS)(LegalView.as_view()), name="legal"),
    url(r"general-business-terms/$", cache_page(CACHE_MIDDLEWARE_SECONDS)(GBTView.as_view()), name="gbt"),
    url(r"cancellation-policy/$", cache_page(CACHE_MIDDLEWARE_SECONDS)(CancellationPolicyView.as_view()), name="cancellation-policy"),
    url(r"privacy-policy/$", cache_page(CACHE_MIDDLEWARE_SECONDS)(PrivacyPolicyView.as_view()), name="privacy-policy"),
    url(r"^(?P<site>[a-zA-Z0-9_.-]+)/$", cache_page(CACHE_MIDDLEWARE_SECONDS)(GenericView.as_view()), name="generic_cms_page")
]
