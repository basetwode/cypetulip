from django.conf.urls import include, url
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

from home.settings import CACHE_MIDDLEWARE_SECONDS
from shop.views.authentication_views import *
from shop.views.product_views import *
from shop.views.shoppingcart_views import *
from shop.views.account_views import *

__author__ = ''
app_name = 'shop'

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^index/$', IndexView.as_view()),
    url(r'^$', RedirectView.as_view(url='/cms/home/'), name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^companies/create', CompanyView.create, name='create-company'),
    url(r'^logout/', LogoutView.as_view()),

    # todo: use uuid ?
    url(r'^cart/$', ShoppingCartDetailView.as_view(), name="shoppingcart_cart"),
    # todo: must include category path
    url(r'^cart/(?P<path>[\S0-9_.-\\s\- ]*)/(?P<name>[\S0-9_.-\\s\- ]*)/add/$', ShoppingCartAddItemView.as_view(), name="shoppingcart_add"),
    # todo: whats the second one for?
    url(r'^cart/delivery/(?P<uuid>[a-zA-Z0-9\\s\-_ ]+)/$', DeliveryView.as_view(), name="delivery_order"),
    url(r'^cart/confirmed/(?P<uuid>[a-zA-Z0-9\\s\-_ ]+)/$', OrderConfirmedView.as_view(), name="confirmed_order"),


    url(r'^products/$', ProductView.as_view(), name="products"), # ProductsOverview und name dann prodcuts_overview
    url(r'^products/(?P<category>[\S0-9_.-\\s\- ]*)$', ProductView.as_view(), name="products"),
    url(r"^products/(?P<category>[\S0-9_.-\\s\- ]*)/(?P<product>[\S0-9_.-\\s\- ]+)$",
        cache_page(CACHE_MIDDLEWARE_SECONDS)(ProductDetailView.as_view()),name='product_detail'),
    url(r"^products/(?P<product>[\S0-9_.-\\s\- ]+)/order/(?P<order_step>[0-9]+)$", OrderView.as_view()),

    url(r'^myaccount/$', MyAccountView.as_view(), name="my_account"),
    url(r'^myaccount/password_change/$', PasswordChangeViewCustomer.as_view(), name="password_change"),

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

    url(r'offer/(?P<product>[\S0-9_.-\\s\- ]+)$', IndividualOfferView.as_view(), name="individual_offer"),

]
