from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from shop.authentification.views import (CompanyView, LoginView, LogoutView,
                                         RegisterView)
from shop.my_account.views import (AccountSettingsView, CompanySettingsView,
                                   MyAccountView, OrderDetailView, OrdersView,
                                   SearchOrders, AddressCreationView, AddressEditView, AddressDeleteView,
                                   AddressOverviewView)
from shop.order.checkout import DeliveryView
from shop.order.overview import OverviewView
from shop.order.shoppingcart import ShoppingCartDetailView, ShoppingCartView
from shop.views import *

__author__ = ''
app_name = 'shop'

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^index/$', IndexView.as_view()),
    url(r'^$', RedirectView.as_view(url='/cms/home/'), name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^register/$', RegisterView.signup, name='register'),
    url(r'^companies/create', CompanyView.create, name='create-company'),
    url(r'^logout/', LogoutView.as_view()),

    url(r'^cart/add/(?P<product>[\S0-9_.-\\s\- ]*)$', ShoppingCartView.as_view()),
    url(r'^cart/remove/([0-9]*)$', ShoppingCartDetailView.as_view()),
    url(r'^cart/', ShoppingCartDetailView.as_view(), name="shopping_cart"),
    url(r'^delivery/remove/([0-9]*)$', DeliveryView.as_view()),
    url(r'^delivery/(?P<order>[\S0-9_.-\\s\- ]*)$', DeliveryView.as_view(), name="delivery_order"),
    url(r'^confirmed/(?P<order>[a-zA-Z0-9\\s\-_ ]+)$', OrderConfirmedView.as_view(), name="confirmed_order"),
    url(r'^overview/(?P<order>[\S0-9_.-\\s\- ]*)$', OverviewView.as_view(), name="overview_order"),

    url(r'^products/(?P<category>[\S0-9_.-\\s\- ]*)$', ProductView.as_view(), name="products"),
    url(r"^product/(?P<product>[\S0-9_.-\\s\- ]+)$", ProductDetailView.as_view()),
    url(r"^product/(?P<product>[\S0-9_.-\\s\- ]+)/order/(?P<order_step>[0-9]+)$", OrderView.as_view()),

    url(r'^myaccount/$', MyAccountView.as_view(), name="my_account"),

    url(r'^myaccount/address/create/$', AddressCreationView.as_view(), name="address_create"),
    url(r'^myaccount/address/(?P<address_id>[a-zA-Z0-9_.-]+)/$', AddressEditView.as_view(), name="address_edit"),
    url(r'^myaccount/address/(?P<url_param>[a-zA-Z0-9_.-]+)/delete$', AddressDeleteView.as_view(),
        name="address_delete"),
    url(r'^myaccount/address/$', AddressOverviewView.as_view(), name="address_overview"),

    url(r'^myaccount/account_settings/$', AccountSettingsView.as_view(), name="account_settings"),
    url(r'^myaccount/company_settings/$', CompanySettingsView.as_view(), name="company_settings"),

    url(r'^myaccount/orders(/(?P<number_of_orders>[0-9]*)/(?P<page>[0-9]*))?/$', OrdersView.as_view(),
        name="all_orders"),
    url(r'orders/search/', SearchOrders.as_view(), name="search_orders"),

    url(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\-_ ]+)/$', OrderDetailView.as_view(), name="detail_order"),
    url(r'^myaccount/orders/([a-zA-Z0-9\\s\-_ ]+)/cancel/$', OrderCancelView.as_view(),
        name="detail_order_cancel_order"),
    url(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\-_ ]+)/bill/show$', OrderDetailView.as_view(),
        name="detail_order_show_bill"),
    url(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\-_ ]+)/review/create$', OrderDetailView.as_view(),
        name="detail_order_write_review"),

    url(r'^password_change/$', auth_views.PasswordChangeView.as_view(), name='password_change'),
    url(r'^password_change/done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[\S0-9_.-\\s\- ]*)/(?P<token>[\S0-9_.-\\s\- ]*)/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
