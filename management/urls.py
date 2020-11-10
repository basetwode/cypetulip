from django.conf.urls import url
from django.urls import include

from management.views import (CategoriesOverviewView, CategoryCreationView,
                              CategoryEditView, CustomersOverviewView, LdapSettingsDetailView,
                              MailSettingsDetailView,
                              ManagementOrderDetailView,
                              ManagementOrderOverviewView, ManagementView,
                              PageCreateView, PageEditView, PagesOverviewView,
                              ProductCreationView, ProductEditView,
                              ProductsOverviewView, SectionCreateView,
                              SectionEditView, SectionsOverviewView,
                              SettingsView, ProductDeleteView, SectionDeleteView, PageDeleteView, CategoryDeleteView,
                              ContactEditView, CompanyEditView, LegalSettingsDetailView, EmployeeOverviewView,
                              EmployeeCreationView, OrderAssignEmployeeView, OrderPayView,
                              OrderShipView, OrderChangeStateView, ShipmentOverviewView,
                              SubItemOverviewView, SubItemDeleteView,
                              OrderAcceptInvoiceView, DeleteIndividualOfferRequest, IndividualOfferRequestOverview,
                              IndividualOfferRequestView, CreateOrderView, CreateOrderDetailView, CreateOrderItem,
                              DeleteOrderItem, DeleteOrder, ShopSettingsDetailView, PaymentProviderSettings,
                              HeaderCreateView, HeaderEditView, HeadersOverviewView, HeaderDeleteView, FooterCreateView,
                              FooterDeleteView, FooterEditView, FootersOverviewView, NumberSubItemCreateUpdateView,
                              FileSubItemCreationView, CheckboxSubItemCreateUpdateView, SelectSubItemCreationView,
                              SelectItemCreationView, SelectItemDeleteView)
from shop.my_account.views import SearchOrders, SearchCustomers

__author__ = ''

from shop.views import OrderCancelView

urlpatterns = [
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^$', ManagementView.as_view(), name="management_index"),
    url(r'^settings/$', SettingsView.as_view()),
    url(r'^shipments/$', ShipmentOverviewView.as_view(), name="all_shipments"),

    url(r'^orders(/(?P<number_of_orders>[0-9]*)/(?P<page>[0-9]*))?/$', ManagementOrderOverviewView.as_view(),
        name="management_all_orders"),

    url(r"^settings/mail/(?P<mail_settings_id>[a-zA-Z0-9_.-]*)$", MailSettingsDetailView.as_view(),
        name='mail_settings_details'),
    url(r"^settings/ldap/(?P<ldap_settings_id>[a-zA-Z0-9_.-]*)$", LdapSettingsDetailView.as_view(),
        name='ldap_settings_details'),
    url(r"^settings/legal/(?P<legal_settings_id>[a-zA-Z0-9_.-]*)$", LegalSettingsDetailView.as_view(),
        name='legal_settings_details'),
    url(r"^settings/shop/(?P<shop_settings_id>[a-zA-Z0-9_.-]*)$", ShopSettingsDetailView.as_view(),
        name='shop_settings_details'),
    url(r"^settings/payment/$", PaymentProviderSettings.as_view(),
        name='payment_settings_details'),

    url(r'orders/search/', SearchOrders.as_view(), name="search_orders"),
    url(r'^orders/(?P<order>[a-zA-Z0-9\\s\-_ ]+)$', ManagementOrderDetailView.as_view(),
        name="management_detail_order"),

    url(r'^categories/create/$', CategoryCreationView.as_view(), name="create_category"),
    url(r'^categories/(?P<category_id>[a-zA-Z0-9_.-]+)/$', CategoryEditView.as_view(), name="category_edit"),
    url(r'^categories/(?P<url_param>[a-zA-Z0-9_.-]+)/delete$', CategoryDeleteView.as_view(), name="category_delete"),
    url(r'^categories/$', CategoriesOverviewView.as_view(), name="categories_overview"),

    url(r'^products/create/$', ProductCreationView.as_view(), name="create_product"),
    url(r'^products/(?P<product_id>[a-zA-Z0-9_.-]+)/$', ProductEditView.as_view(), name="product_edit"),
    url(r'^products/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', ProductDeleteView.as_view(), name="product_delete"),
    url(r'^products/$', ProductsOverviewView.as_view(), name="products_overview"),

    url(r'^filesubitem/(?P<subitem_id>[0-9]*)/$', FileSubItemCreationView.as_view(), name="filesubitem_create"),
    url(r'^numbersubitem/(?P<subitem_id>[0-9]*)/$', NumberSubItemCreateUpdateView.as_view(), name="numbersubitem_create"),
    url(r'^checkboxsubitem/(?P<subitem_id>[0-9]*)/$', CheckboxSubItemCreateUpdateView.as_view(), name="checkboxsubitem_create"),
    url(r'^selectsubitem/(?P<subitem_id>[0-9]*)/$', SelectSubItemCreationView.as_view(), name="selectsubitem_create"),
    url(r'^selectitem/(?P<parent_id>[0-9]*)/(?P<id>[0-9]*)$', SelectItemCreationView.as_view(), name="selectitem_create"),
    url(r'^selectitem/(?P<parent_id>[0-9]*)/(?P<id>[0-9]*)/delete$', SelectItemDeleteView.as_view(), name="selectitem_delete"),

    url(r'^subitems/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', SubItemDeleteView.as_view(),
        name="subitem_delete"),
    url(r'^subitems/$', SubItemOverviewView.as_view(), name="subitem_overview"),

    url(r'^customers/$', CustomersOverviewView.as_view(), name="customers_overview"),
    url(r'^customers/search/$', SearchCustomers.as_view(), name="search_customers"),
    url(r'^contacts/(?P<contact_id>[a-zA-Z0-9_.-]+)/$', ContactEditView.as_view(), name="contact_edit"),
    url(r'^companies/(?P<company_id>[a-zA-Z0-9_.-]+)/$', CompanyEditView.as_view(), name="company_edit"),

    url(r'^pages/create/$', PageCreateView.as_view(), name="create_page"),
    url(r'^pages/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', PageDeleteView.as_view(), name="page_delete"),
    url(r'^pages/$', PagesOverviewView.as_view(), name="pages"),
    url(r'^pages/(?P<page_id>[a-zA-Z0-9_.-]+)/$', PageEditView.as_view(), name="page_edit"),

    url(r'^sections/create/$', SectionCreateView.as_view(), name="create_section"),
    url(r'^sections/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', SectionDeleteView.as_view(), name="section_delete"),
    url(r'^sections/$', SectionsOverviewView.as_view(), name="sections"),
    url(r'^sections/(?P<section_id>[a-zA-Z0-9_.-]+)/$', SectionEditView.as_view(), name="section_edit"),

    url(r'^headers/create/$', HeaderCreateView.as_view(), name="header_create"),
    url(r'^headers/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', HeaderDeleteView.as_view(), name="header_delete"),
    url(r'^headers/$', HeadersOverviewView.as_view(), name="headers_overview"),
    url(r'^headers/(?P<header_id>[a-zA-Z0-9_.-]+)/$', HeaderEditView.as_view(), name="header_edit"),

    url(r'^footers/create/$', FooterCreateView.as_view(), name="footer_create"),
    url(r'^footers/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', FooterDeleteView.as_view(), name="footer_delete"),
    url(r'^footers/$', FootersOverviewView.as_view(), name="footers_overview"),
    url(r'^footers/(?P<footer_id>[a-zA-Z0-9_.-]+)/$', FooterEditView.as_view(), name="footer_edit"),

    url(r'^employees/$', EmployeeOverviewView.as_view(), name="employee_overview"),
    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/assign/$',
        OrderAssignEmployeeView.as_view(), name="assign_employee"),
    url(r'^orders/create/(?P<id>[a-zA-Z0-9\\s\-_ ]*)$',
        CreateOrderView.as_view(), name="create_order"),
    url(r'^orders/detail/create/(?P<parent_id>[0-9]+)/(?P<id>[a-zA-Z0-9\\s\-_ ]*)$',
        CreateOrderDetailView.as_view(), name="create_order_detail"),
    url(r'^orders/item/create/(?P<parent_id>[0-9]+)/(?P<id>[a-zA-Z0-9\\s\-_ ]*)$',
        CreateOrderItem.as_view(), name="create_order_item"),
    url(r'^orders/item/delete/(?P<parent_id>[0-9]+)/(?P<id>[a-zA-Z0-9\\s\-_ ]*)$',
        DeleteOrderItem.as_view(), name="delete_order_item"),

    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/cancel/$',
        OrderCancelView.as_view(), name="cancel_order"),
    url(r'^orders/(?P<order_hash>[a-zA-Z0-9\\s\-_ ]+)/delete/$',
        DeleteOrder.as_view(), name="delete_order"),
    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/pay/$',
        OrderPayView.as_view(), name="pay_order"),
    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/ship/$',
        OrderShipView.as_view(), name="ship_order"),
    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/states/change$',
        OrderChangeStateView.as_view(), name="change_state_order"),
    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/accept$',
        OrderAcceptInvoiceView.as_view(), name="accept_order"),

    url(r'^offers/$', IndividualOfferRequestOverview.as_view(), name="individualoffers_overview"),
    url(r'^offers/(?P<offer_id>[a-zA-Z0-9\\s\-_ ]+)/$', IndividualOfferRequestView.as_view(), name="individualoffer_view"),
    url(r'^offers/(?P<offer_id>[a-zA-Z0-9\\s\-_ ]+)/delete$',
        DeleteIndividualOfferRequest.as_view(), name="individualoffer_delete"),

    url(r'^employees/create/$', EmployeeCreationView.as_view(), name="create_employee"),

]
