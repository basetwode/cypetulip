from django.urls import include, re_path

from cms.api import routes
from cms.views.main import *

__author__ = ''

app_name = 'cms'

urlpatterns = [
    re_path(r'^api/v1/', include(routes.router.urls)),
    re_path(r'^admin/$', AdminView.as_view()),
    re_path(r'^permissions-denied/$', PermissionDeniedView.as_view(), name='permissions_denied'),
    re_path(r'^css-setting/(?P<css_settings_id>[a-zA-Z0-9_.-]*)$', CSSSettingsView.as_view(), name='css-settings'),
    re_path(r"contact/$", ContactView.as_view(), name="contact"),
    re_path(r"legal/$", LegalView.as_view(), name="legal"),
    re_path(r"general-business-terms/$", GBTView.as_view(), name="gbt"),
    re_path(r"cancellation-policy/$", CancellationPolicyView.as_view(),
            name="cancellation-policy"),
    re_path(r"privacy-policy/$", PrivacyPolicyView.as_view(), name="privacy-policy"),
    re_path(r"^(?P<site>[a-zA-Z0-9_.-]+)/$", GenericView.as_view(),
            name="generic_cms_page")
]
