from django.urls import include, re_path

from shop.api import routes
from shop.views.account_views import *
from shop.views.authentication_views import *
from shop.views.product_views import *
from shop.views.shoppingcart_views import *

__author__ = ''
app_name = 'shop'

urlpatterns = [
    re_path(r'^api/v1/', include(routes.router.urls)),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^$', RedirectView.as_view(url='/cms/home/'), name='home'),
    re_path(r'^login/$', LoginAuthenticationView.as_view(), name='login'),
    re_path(r'^register/$', RegisterView.as_view(), name='register'),
    re_path(r'^companies/create', CompanyView.create, name='create-company'),
    re_path(r'^logout/', LogoutView.as_view()),

    re_path(r'^cart/$', ShoppingCartDetailView.as_view(), name="shoppingcart_cart"),
    re_path(r'^cart/(?P<path>[\S0-9_.-\\s\- ]*)/(?P<name>[\S0-9_.-\\s\- ]*)/add/$', ShoppingCartAddItemView.as_view(),
            name="shoppingcart_add"),
    re_path(r'^cart/delivery/(?P<uuid>[a-zA-Z0-9\\s\-_ ]+)/$', DeliveryView.as_view(), name="delivery_order"),
    re_path(r'^cart/confirmed/(?P<uuid>[a-zA-Z0-9\\s\-_ ]+)/$', OrderConfirmedView.as_view(), name="confirmed_order"),

    re_path(r'^products/$', ProductView.as_view(), name="products"),  # ProductsOverview und name dann prodcuts_overview
    re_path(r"^products/(?P<category>[\S0-9_.-\\s\- ]*)/(?P<product>[\S0-9_.-\\s\- ]+)$",
            ProductDetailView.as_view(), name='product_detail'),
    re_path(r'^products/(?P<category>[\S0-9_.-\\s\- ]*)$', ProductView.as_view(), name="products"),

    re_path(r'^myaccount/$', MyAccountView.as_view(), name="my_account"),
    re_path(r'^myaccount/password_change/$', PasswordChangeViewCustomer.as_view(), name="password_change"),

    re_path(r'^myaccount/address/create/$', AddressCreationView.as_view(), name="address_create"),
    re_path(r'^myaccount/address/(?P<address_id>[a-zA-Z0-9_.-]+)/$', AddressEditView.as_view(), name="address_edit"),
    re_path(r'^myaccount/address/(?P<url_param>[a-zA-Z0-9_.-]+)/delete$', AddressDeleteView.as_view(),
            name="address_delete"),
    re_path(r'^myaccount/address/$', AddressOverviewView.as_view(), name="address_overview"),

    re_path(r'^myaccount/account_settings/$', AccountSettingsView.as_view(), name="account_settings"),
    re_path(r'^myaccount/company_settings/$', CompanySettingsView.as_view(), name="company_settings"),

    re_path(r'^myaccount/orders(/(?P<number_of_orders>[0-9]*)/(?P<page>[0-9]*))?/$', OrdersView.as_view(),
            name="all_orders"),
    re_path(r'orders/search/', SearchOrders.as_view(), name="search_orders"),

    re_path(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\-_ ]+)/$', OrderDetailView.as_view(), name="detail_order"),
    re_path(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\-_ ]+)/cancel/$', OrderCancelView.as_view(),
            name="detail_order_cancel_order"),
    re_path(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\-_ ]+)/bill/show$', OrderDetailView.as_view(),
            name="detail_order_show_bill"),
    re_path(r'^myaccount/orders/(?P<order>[a-zA-Z0-9\\s\-_ ]+)/review/create$', OrderDetailView.as_view(),
            name="detail_order_write_review"),

    re_path(r'offer/(?P<category>[\S0-9_.-\\s\- ]*)/(?P<product>[\S0-9_.-\\s\- ]+)$', IndividualOfferView.as_view(),
            name="individual_offer"),

]
