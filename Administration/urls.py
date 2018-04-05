from Administration.views import SettingsDetailView, SettingsView, AdminView, AdminOrderOverviewView, \
    AdminOrderDetailView
from django.conf.urls import url

from Shop.my_account.views import SearchOrders

__author__ = ''


urlpatterns = [
    url(r'^$', AdminView.as_view(),name="admin_index"),
    url(r'^settings/$', SettingsView.as_view()),
    url(r'^orders(/(?P<number_of_orders>[0-9]*)/(?P<page>[0-9]*))?/$', AdminOrderOverviewView.as_view(), name="admin_all_orders"),
    url(r"^settings/(?P<app_name>[a-zA-Z0-9_.-]+)$", SettingsDetailView.as_view()),
    url(r'^orders/search/', SearchOrders.as_view(), name="search_orders"),
    url(r'^orders/(?P<order>[a-zA-Z0-9\\s\- ]+)/$', AdminOrderDetailView.as_view(), name="admin_detail_order"),

]