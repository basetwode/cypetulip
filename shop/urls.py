from django.contrib.auth import logout


from shop.authentification.views import LoginView, LogoutView, RegisterView
from shop.my_account.views import OrderDetailView, OrdersView, MyAccountView, SearchOrders, AccountSettingsView, \
    CompanySettingsView
from shop.order.overview import OverviewView
from shop.order.shoppingcart import ShoppingCartView,ShoppingCartDetailView
from shop.order.checkout import CheckoutView
from shop.views import *
from django.conf.urls import url, include

__author__ = ''

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^index/', IndexView.as_view()),
    url(r'^login/', LoginView.as_view()),
    url(r'^register/', RegisterView.signup, name='register'),
    url(r'^logout/',  LogoutView.as_view()),

    url(r'^cart/add/(?P<product>[\S0-9_.-\\s\- ]*)$', ShoppingCartView.as_view()),
    url(r'^cart/', ShoppingCartDetailView.as_view()),
    url(r'^checkout/(?P<order>[\S0-9_.-\\s\- ]*)$', CheckoutView.as_view(),name="checkout_order"),
    url(r'^confirmed/(?P<order>[\S0-9_.-\\s\- ]*)$', OrderConfirmedView.as_view(), name="confirmed_order"),
    url(r'^overview/(?P<order>[\S0-9_.-\\s\- ]*)$', OverviewView.as_view(), name="overview_order"),

    url(r'^products/(?P<category>[\S0-9_.-\\s\- ]*)$', ProductView.as_view()),
    url(r"^product/(?P<product>[\S0-9_.-\\s\- ]+)$", ProductDetailView.as_view()),
    url(r"^product/(?P<product>[\S0-9_.-\\s\- ]+)/order/(?P<order_step>[0-9]+)$", OrderView.as_view()),

    url(r'^myaccount/$', MyAccountView.as_view(), name="my_account"),

    url(r'^myaccount/account_settings/$', AccountSettingsView.as_view(), name="account_settings"),
    url(r'^myaccount/company_settings/$', CompanySettingsView.as_view(), name="company_settings"),

    url(r'^myaccount/orders(/(?P<number_of_orders>[0-9]*)/(?P<page>[0-9]*))?/$', OrdersView.as_view(), name="all_orders"),
    url(r'^myaccount/orders/search/', SearchOrders.as_view(), name="search_orders"),

    url(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\- ]+)/$', OrderDetailView.as_view(), name="detail_order"),
    url(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\- ]+)/c_order/$', OrderDetailView.as_view(),name="detail_order_cancel_order"),
    url(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\- ]+)/s_bill/$', OrderDetailView.as_view(),name="detail_order_show_bill"),
    url(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\- ]+)/w_review$', OrderDetailView.as_view(),name="detail_order_write_review"),
]

