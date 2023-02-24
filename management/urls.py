from django.urls import include, re_path

from management.api import routes
from management.views.account_views import CustomersOverview, MergeAccounts, CompanyCreationView, CompanyDeleteView, \
    AddressCreationView, AddressDeleteView, ContactCreationView, ContactDeleteView, ContactResetPwdView, \
    CustomerImportView
from management.views.categories_views import CategoryCreationView, CategoryEditView, CategoryDeleteView
from management.views.cms_views import CategoriesOverview, PageCreateView, PageDeleteView, PagesOverview, \
    PageEditView, SectionCreateView, SectionDeleteView, SectionsOverviewView, SectionEditView, HeaderCreateView, \
    HeaderDeleteView, HeadersOverviewView, HeaderEditView, FooterCreateView, FooterDeleteView, FootersOverviewView, \
    FooterEditView
from management.views.communication_views import CommmunicationView, CommmunicationDetailView, CommmunicationRetryView
from management.views.discounts_views import PercentageDiscountEditView, FixedAmountDiscountEditView, DiscountOverview
from management.views.employees_views import EmployeeOverviewView, EmployeeCreationView
from management.views.main import ManagementView
from management.views.offers_views import IndividualOfferRequestOverview, IndividualOfferRequestView, \
    DeleteIndividualOfferRequest
from management.views.orders_views import ManagementOrderOverview, ManagementOrderDetailView, OrderAssignEmployeeView, \
    OrderCreateView, DeleteOrder, OrderPayView, OrderShipView, OrderChangeStateView, OrderAcceptInvoiceView, \
    ManagementFullExport, ManagementOrderExportCSV, OrderCancelView
from management.views.products_views import ProductCreationView, ProductEditView, ProductDeleteView, \
    ProductsOverview, FileSubItemCreationView, NumberSubItemCreateUpdateView, CheckboxSubItemCreateUpdateView, \
    SelectSubItemCreationView, SelectItemCreationView, SelectItemDeleteView, SubItemDeleteView, SubItemOverview, \
    AttributeTypeDeleteView, AttributeTypeEditView, AttributeTypeCreationView, AttributeTypeOverview
from management.views.settings_views import MailSettingsDetailView, LdapSettingsDetailView, LegalSettingsDetailView, \
    ShopSettingsDetailView, PaymentProviderSettings, CacheManagementView
from management.views.shipments_views import ShipmentOverview
from shop.views.account_views import SearchOrders, SearchCustomers

urlpatterns = [
    re_path(r'^tinymce/', include('tinymce.urls')),
    re_path(r'^$', ManagementView.as_view(), name="management_index"),
    re_path(r'^api/v1/', include(routes.router.urls)),
    re_path(r'^shipments/$', ShipmentOverview.as_view(), name="shipments_overview"),

    re_path(r'^orders(/(?P<number_of_orders>[0-9]*)/(?P<page>[0-9]*))?/$', ManagementOrderOverview.as_view(),
            name="management_orders_overview"),

    re_path(r"^settings/mail/(?P<id>[a-zA-Z0-9_.-]*)$", MailSettingsDetailView.as_view(),
            name='mail_settings_details'),
    re_path(r"^settings/ldap/(?P<id>[a-zA-Z0-9_.-]*)$", LdapSettingsDetailView.as_view(),
            name='ldap_settings_details'),
    re_path(r"^settings/legal/(?P<id>[a-zA-Z0-9_.-]*)$", LegalSettingsDetailView.as_view(),
            name='legal_settings_details'),
    re_path(r"^settings/shop/(?P<id>[a-zA-Z0-9_.-]*)$", ShopSettingsDetailView.as_view(),
            name='shop_settings_details'),
    re_path(r"^settings/payment/$", PaymentProviderSettings.as_view(),
            name='payment_settings_details'),
    re_path(r"^settings/cache/$", CacheManagementView.as_view(),
            name='cache_settings_details'),

    re_path(r"^communication/$", CommmunicationView.as_view(),
            name='management_communication_view'),
    re_path(r"^communication/(?P<uuid>[a-zA-Z0-9\\s\-_ ]*)/$", CommmunicationDetailView.as_view(),
            name='management_communication_detail_view'),
    re_path(r"^communication/(?P<uuid>[a-zA-Z0-9\\s\-_ ]*)/$", CommmunicationRetryView.as_view(),
            name='management_communication_retry_view'),

    re_path(r'orders/search/', SearchOrders.as_view(), name="orders_search"),
    re_path(r'^orders/(?P<uuid>[a-zA-Z0-9\\s\-_ ]+)$', ManagementOrderDetailView.as_view(),
            name="management_order_detail_view"),

    re_path(r'^categories/create/$', CategoryCreationView.as_view(), name="category_create_view"),
    re_path(r'^categories/(?P<id>[a-zA-Z0-9_.-]+)/$', CategoryEditView.as_view(), name="category_edit_view"),
    re_path(r'^categories/(?P<url_param>[a-zA-Z0-9_.-]+)/delete$', CategoryDeleteView.as_view(),
            name="category_delete_view"),
    re_path(r'^categories/$', CategoriesOverview.as_view(), name="categories_overview"),

    re_path(r'^products/create/$', ProductCreationView.as_view(), name="product_create_view"),
    re_path(r'^products/(?P<product_id>[a-zA-Z0-9_.-]+)/$', ProductEditView.as_view(), name="product_edit_view"),
    re_path(r'^products/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', ProductDeleteView.as_view(),
            name="product_delete_view"),
    re_path(r'^products/$', ProductsOverview.as_view(), name="products_overview"),
    re_path(r'^attributetypes/$', AttributeTypeOverview.as_view(), name="attribute_types_overview"),
    re_path(r'^attributetypes/create/$', AttributeTypeCreationView.as_view(), name="attribute_types_create_view"),
    re_path(r'^attributetypes/edit/(?P<id>[0-9]*)$', AttributeTypeEditView.as_view(), name="attribute_types_edit_view"),
    re_path(r'^attributetypes/delete/(?P<url_param>[0-9]*)$', AttributeTypeDeleteView.as_view(),
            name="attribute_types_delete_view"),

    re_path(r'^filesubitem/(?P<id>[0-9]*)$', FileSubItemCreationView.as_view(), name="filesubitem_create"),
    re_path(r'^numbersubitem/(?P<id>[0-9]*)$', NumberSubItemCreateUpdateView.as_view(),
            name="idnumbersubitem_create_view"),
    re_path(r'^checkboxsubitem/(?P<id>[0-9]*)$', CheckboxSubItemCreateUpdateView.as_view(),
            name="checkboxsubitem_create_view"),
    re_path(r'^selectsubitem/(?P<id>[0-9]*)$', SelectSubItemCreationView.as_view(), name="selectsubitem_create_view"),
    re_path(r'^selectitem/(?P<parent_id>[0-9]*)/(?P<id>[0-9]*)$', SelectItemCreationView.as_view(),
            name="selectitem_create_view"),
    re_path(r'^selectitem/(?P<parent_id>[0-9]*)/(?P<id>[0-9]*)/delete$', SelectItemDeleteView.as_view(),
            name="selectitem_delete"),

    re_path(r'^subitems/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', SubItemDeleteView.as_view(),
            name="subitem_delete"),
    re_path(r'^subitems/$', SubItemOverview.as_view(), name="subitem_overview"),

    re_path(r'^customers/$', CustomersOverview.as_view(), name="customers_overview"),
    re_path(r'^customers/merge/(?P<id>[0-9]*)/$', MergeAccounts.as_view(), name="customers_merge_view"),
    re_path(r'^customers/search/$', SearchCustomers.as_view(), name="search_customers"),

    re_path(r'^pages/create/$', PageCreateView.as_view(), name="page_create_view"),
    re_path(r'^pages/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', PageDeleteView.as_view(), name="page_delete_view"),
    re_path(r'^pages/$', PagesOverview.as_view(), name="pages_overview"),
    re_path(r'^pages/(?P<page_id>[a-zA-Z0-9_.-]+)/$', PageEditView.as_view(), name="page_edit_view"),

    re_path(r'^sections/create/$', SectionCreateView.as_view(), name="section_create_view"),
    re_path(r'^sections/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', SectionDeleteView.as_view(),
            name="ssection_delete_view"),
    re_path(r'^sections/$', SectionsOverviewView.as_view(), name="sections_overview"),
    re_path(r'^sections/(?P<id>[a-zA-Z0-9_.-]+)/$', SectionEditView.as_view(), name="section_edit_view"),

    re_path(r'^headers/create/$', HeaderCreateView.as_view(), name="header_create"),
    re_path(r'^headers/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', HeaderDeleteView.as_view(), name="header_delete"),
    re_path(r'^headers/$', HeadersOverviewView.as_view(), name="headers_overview"),
    re_path(r'^headers/(?P<id>[a-zA-Z0-9_.-]+)/$', HeaderEditView.as_view(), name="header_edit"),

    re_path(r'^footers/create/$', FooterCreateView.as_view(), name="footer_create"),
    re_path(r'^footers/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', FooterDeleteView.as_view(), name="footer_delete"),
    re_path(r'^footers/$', FootersOverviewView.as_view(), name="footers_overview"),
    re_path(r'^footers/(?P<id>[a-zA-Z0-9_.-]+)/$', FooterEditView.as_view(), name="footer_edit"),

    re_path(r'^employees/$', EmployeeOverviewView.as_view(), name="employees_overview"),
    re_path(r'^employees/create/$', EmployeeCreationView.as_view(), name="employee_create_view"),

    re_path(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/assign/$',
            OrderAssignEmployeeView.as_view(), name="order_assign_employee_view"),
    re_path(r'^orders/create/(?P<uuid>[a-zA-Z0-9\\s\-_ ]*)/$', OrderCreateView.as_view(),
            name="order_update_view"),
    re_path(r'^orders/create/$', OrderCreateView.as_view(),
            name="order_create_view"),

    re_path(r'^orders/(?P<uuid>[a-zA-Z0-9\\s\-_ ]+)/cancel$',
            OrderCancelView.as_view(), name="management_order_cancel_view"),
    re_path(r'^orders/(?P<uuid>[a-zA-Z0-9\\s\-_ ]+)/delete/$',
            DeleteOrder.as_view(), name="order_delete_view"),
    re_path(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/pay/$',
            OrderPayView.as_view(), name="order_pay_view"),
    re_path(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/ship/$',
            OrderShipView.as_view(), name="order_ship_view"),
    re_path(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/states/change$',
            OrderChangeStateView.as_view(), name="order_change_state_view"),
    re_path(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/accept$',
            OrderAcceptInvoiceView.as_view(), name="order_accept_view"),

    re_path(r'^export/csv/$', ManagementOrderExportCSV.as_view(), name="export_csv"),
    re_path(r'^export/full/$', ManagementFullExport.as_view(), name="export"),

    re_path(r'^offers/$', IndividualOfferRequestOverview.as_view(), name="individualoffers_overview"),
    re_path(r'^offers/(?P<id>[a-zA-Z0-9\\s\-_ ]+)/$', IndividualOfferRequestView.as_view(),
            name="individualofferrequest_view"),
    re_path(r'^offers/(?P<id>[a-zA-Z0-9\\s\-_ ]+)/delete$',
            DeleteIndividualOfferRequest.as_view(), name="individualoffer_delete_view"),

    re_path(r'^company/create/(?P<id>[a-zA-Z0-9\\s\-_ ]*)$',
            CompanyCreationView.as_view(), name="company_create_view"),
    re_path(r'^company/(?P<url_param>[a-zA-Z0-9\\s\-_ ]*)/delete/$',
            CompanyDeleteView.as_view(), name="company_delete_view"),
    re_path(r'^address/create/(?P<parent_id>[0-9]+)/(?P<id>[a-zA-Z0-9\\s\-_ ]*)$',
            AddressCreationView.as_view(), name="address_create_view"),
    re_path(r'^address/delete/(?P<parent_id>[0-9]+)/(?P<id>[a-zA-Z0-9\\s\-_ ]*)$',
            AddressDeleteView.as_view(), name="address_delete_view"),
    re_path(r'^contact/create/(?P<parent_id>[0-9]+)/(?P<id>[a-zA-Z0-9\\s\-_ ]*)$',
            ContactCreationView.as_view(), name="contact_create_view"),
    re_path(r'^contact/delete/(?P<parent_id>[0-9]+)/(?P<id>[a-zA-Z0-9\\s\-_ ]*)$',
            ContactDeleteView.as_view(), name="contact_delete_view"),
    re_path(r'^contact/pwd/(?P<id>[a-zA-Z0-9\\s\-_ ]*)$',
            ContactResetPwdView.as_view(), name="contact_pwd_reset_view"),
    re_path(r'^contact/import/$', CustomerImportView.as_view(), name="customer_import_view"),

    re_path(r'^discount/percentage/create/(?P<id>[a-zA-Z0-9_.-]*)$', PercentageDiscountEditView.as_view(),
            name="percentage_discount_edit_view"),
    re_path(r'^discount/fixed/create/(?P<id>[a-zA-Z0-9_.-]*)$', FixedAmountDiscountEditView.as_view(),
            name="fixed_discount_edit_view"),
    re_path(r'^discount/$', DiscountOverview.as_view(), name="discount_overview"),

]
