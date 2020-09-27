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
                              EmployeeCreationView, OrderAssignEmployeeView, AccountingView, OrderPayView,
                              OrderShipView, OrderChangeStateView, ShipmentOverviewView, FileSubItemCreationView,
                              FileSubItemEditView, FileSubItemOverviewView, FileSubItemDeleteView)
from shop.my_account.views import SearchOrders, SearchCustomers

__author__ = ''

from shop.views import OrderCancelView

urlpatterns = [
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^$', ManagementView.as_view(), name="management_index"),
    url(r'^settings/$', SettingsView.as_view()),
    url(r'^accounting/$', AccountingView.as_view(), name="accounting"),
    url(r'^shipments/$', ShipmentOverviewView.as_view(), name="all_shipments"),

    url(r'^orders(/(?P<number_of_orders>[0-9]*)/(?P<page>[0-9]*))?/$', ManagementOrderOverviewView.as_view(),
        name="management_all_orders"),

    url(r"^settings/mail/(?P<mail_settings_id>[a-zA-Z0-9_.-]*)$", MailSettingsDetailView.as_view(),
        name='mail_settings_details'),
    url(r"^settings/ldap/(?P<ldap_settings_id>[a-zA-Z0-9_.-]*)$", LdapSettingsDetailView.as_view(),
        name='ldap_settings_details'),
    url(r"^settings/legal/(?P<legal_settings_id>[a-zA-Z0-9_.-]*)$", LegalSettingsDetailView.as_view(),
        name='legal_settings_details'),

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

    url(r'^filesubitems/create/$', FileSubItemCreationView.as_view(), name="create_filesubitem"),
    url(r'^filesubitems/(?P<filesubitem_id>[a-zA-Z0-9_.-]+)/$', FileSubItemEditView.as_view(), name="filesubitem_edit"),
    url(r'^filesubitems/(?P<url_param>[a-zA-Z0-9_.-]+)/delete/$', FileSubItemDeleteView.as_view(),
        name="filesubitem_delete"),
    url(r'^filesubitems/$', FileSubItemOverviewView.as_view(), name="filesubitem_overview"),

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

    url(r'^employees/$', EmployeeOverviewView.as_view(), name="employee_overview"),
    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/assign/$',
        OrderAssignEmployeeView.as_view(), name="assign_employee"),
    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/cancel/$',
        OrderCancelView.as_view(), name="cancel_order"),
    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/pay/$',
        OrderPayView.as_view(), name="pay_order"),
    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/ship/$',
        OrderShipView.as_view(), name="ship_order"),
    url(r'^orders/([a-zA-Z0-9\\s\-_ ]+)/states/change$',
        OrderChangeStateView.as_view(), name="change_state_order"),

    url(r'^employees/create/$', EmployeeCreationView.as_view(), name="create_employee"),

]
