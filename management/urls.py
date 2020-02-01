from django.conf.urls import url
from django.urls import include

from management.views import (CategoriesOverviewView, CategoryCreationView,
                              CategoryEditView, CustomerCreationView,
                              CustomersOverviewView, LdapSettingsDetailView,
                              MailSettingsDetailView,
                              ManagementOrderDetailView,
                              ManagementOrderOverviewView, ManagementView,
                              PageCreateView, PageEditView, PagesOverviewView,
                              ProductCreationView, ProductEditView,
                              ProductsOverviewView, SectionCreateView,
                              SectionEditView, SectionsOverviewView,
                              SettingsView, ProductDeleteView)
from shop.my_account.views import SearchOrders

__author__ = ''
urlpatterns = [
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^$', ManagementView.as_view(), name="management_index"),
    url(r'^settings/$', SettingsView.as_view()),

    url(r'^orders(/(?P<number_of_orders>[0-9]*)/(?P<page>[0-9]*))?/$', ManagementOrderOverviewView.as_view(),
        name="management_all_orders"),

    url(r"^settings/mail/(?P<mail_settings_id>[a-zA-Z0-9_.-]*)$", MailSettingsDetailView.as_view(),
        name='mail_settings_details'),
    url(r"^settings/ldap/(?P<ldap_settings_id>[a-zA-Z0-9_.-]*)$", LdapSettingsDetailView.as_view(),
        name='ldap_settings_details'),

    url(r'^orders/search/', SearchOrders.as_view(), name="search_orders"),
    url(r'^orders/(?P<order>[a-zA-Z0-9\\s\-_ ]+)$', ManagementOrderDetailView.as_view(),
        name="management_detail_order"),

    url(r'^categories/create/$', CategoryCreationView.as_view(), name="create_category"),
    url(r'^categories/(?P<category_id>[a-zA-Z0-9_.-]+)/$', CategoryEditView.as_view(), name="category_edit"),
    url(r'^categories/$', CategoriesOverviewView.as_view(), name="categories_overview"),

    url(r'^products/create/$', ProductCreationView.as_view(), name="create_product"),
    url(r'^products/(?P<product_id>[a-zA-Z0-9_.-]+)/$', ProductEditView.as_view(), name="product_edit"),
    url(r'^products/(?P<product_id>[a-zA-Z0-9_.-]+)/delete/$', ProductDeleteView.as_view(), name="product_delete"),
    url(r'^products/$', ProductsOverviewView.as_view(), name="products_overview"),

    url(r'^customers/create/$', CustomerCreationView.as_view(), name="create_customer"),
    url(r'^customers/$', CustomersOverviewView.as_view(), name="customers_overview"),

    url(r'^pages/create/$', PageCreateView.as_view(), name="create_page"),
    url(r'^pages/$', PagesOverviewView.as_view(), name="pages"),
    url(r'^pages/(?P<page_id>[a-zA-Z0-9_.-]+)/$', PageEditView.as_view(), name="page_edit"),

    url(r'^sections/create/$', SectionCreateView.as_view(), name="create_section"),
    url(r'^sections/$', SectionsOverviewView.as_view(), name="sections"),
    url(r'^sections/(?P<section_id>[a-zA-Z0-9_.-]+)/$', SectionEditView.as_view(), name="section_edit"),
]
