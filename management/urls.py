from management.views import MailSettingsDetailView, SettingsView, ManagementView, ManagementOrderOverviewView, \
    ManagementOrderDetailView, LdapSettingsDetailView
from django.conf.urls import url

from shop.my_account.views import SearchOrders

__author__ = ''

urlpatterns = [
    url(r'^$', ManagementView.as_view(), name="management_index"),
    url(r'^settings/$', SettingsView.as_view()),
    url(r'^orders(/(?P<number_of_orders>[0-9]*)/(?P<page>[0-9]*))?/$', ManagementOrderOverviewView.as_view(),
        name="management_all_orders"),
    url(r"^settings/mail/(?P<mail_settings_id>[a-zA-Z0-9_.-]*)$", MailSettingsDetailView.as_view(), name='mail_settings_details'),
    url(r"^settings/ldap/(?P<ldap_settings_id>[a-zA-Z0-9_.-]*)$", LdapSettingsDetailView.as_view(), name='ldap_settings_details'),
    url(r'^orders/search/', SearchOrders.as_view(), name="search_orders"),
    url(r'^orders/(?P<order>[a-zA-Z0-9\\s\- ]+)/$', ManagementOrderDetailView.as_view(),
        name="management_detail_order"),
]
