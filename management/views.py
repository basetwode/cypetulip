from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms.widgets import Input
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView

# Create your views here.
from django.views.generic import View, DetailView, ListView, DeleteView

from cms.models import Page, Section
from home.settings import MEDIA_ROOT
from management.models import MailSettings, LdapSettings
from permissions.permissions import check_serve_perms
from shop.models import Contact, Order, OrderItem, Product, ProductCategory
from shop.my_account.views import SearchOrders
from shop.order.utils import get_orderitems_once_only
from utils.views import CreateUpdateView


class ManagementView(View):
    template_name = 'management.html'

    def get(self, request):
        contact = Contact.objects.filter(user=request.user)
        mail_settings = MailSettings.objects.all()
        try:
            company = contact[0].company
            mail_settings = mail_settings[0]
        except IndexError:
            pass
        return render(request, self.template_name, {'contact': contact})

    def post(self, request):
        pass


class ManagementOrderOverviewView(View):
    template_name = 'orders-overview.html'

    def get(self, request, page=1):
        contact = Contact.objects.get(user=request.user)
        _orders, search = SearchOrders.filter_orders(request, True)
        number_of_orders = '5'
        paginator = Paginator(_orders, number_of_orders)
        for order in _orders:
            total = 0
            for order_item in order.orderitem_set.all():
                total += order_item.product.price
            order.total = total
        try:
            _orders = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            _orders = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            _orders = paginator.page(paginator.num_pages)
        return render(request, self.template_name,
                      {'orders': _orders, 'contact': contact, 'search': search})

    @check_serve_perms
    def post(self, request):
        pass


class ManagementOrderDetailView(DetailView):
    template_name = 'order-details.html'
    slug_url_kwarg = 'order'
    slug_field = 'order_hash'

    @check_serve_perms
    def get(self, request, order):
        contact = Contact.objects.get(user=request.user)
        company = contact.company
        _order = Order.objects.get(order_hash=order)
        if _order:
            total = 0
            for order_item in _order.orderitem_set.all():
                total += order_item.product.price
            _order.total = total
            order_items = OrderItem.objects.filter(order=_order, order_item__isnull=True,
                                                   product__in=Product.objects.all())
            return render(request, self.template_name,
                          {'order_details': _order, 'order': _order, 'contact': contact,
                           'order_items': order_items,
                           'order_items_once_only': get_orderitems_once_only(_order)})

    def post(self, request):
        pass


class SettingsView(View):

    def get(self, request):
        # <view logic>
        return HttpResponse('SettingsView')

    def post(self, request):
        # <view logic>
        return HttpResponse('result')


class MailSettingsDetailView(CreateUpdateView):
    template_name = 'settings-details.html'
    mail_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'mail_settings_id'
    model = MailSettings
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('mail_settings_details', kwargs={'mail_settings_id': self.object.id})


class LdapSettingsDetailView(CreateUpdateView):
    template_name = 'settings-details.html'
    ldap_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'ldap_settings_id'
    model = LdapSettings
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('ldap_settings_details', kwargs={'ldap_settings_id': self.object.id})


class CategoriesOverviewView(ListView):
    template_name = 'categories-overview.html'
    context_object_name = 'categories'
    model = ProductCategory


class ProductsOverviewView(ListView):
    template_name = 'products-overview.html'
    context_object_name = 'products'
    model = Product

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['categories'] = ProductCategory.objects.all()
        return context


class CustomersOverviewView(ListView):
    template_name = 'customers/customers-overview.html'
    context_object_name = 'customers'
    model = Contact


class CustomerCreationView(CreateView):
    template_name = 'customers/contact-create.html'
    context_object_name = 'customers'
    model = Contact
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('costumer_edit', kwargs={'costumer_id': self.object.id})


class UserCreationView(CreateView):
    template_name = 'customers/create-modal.html'
    context_object_name = 'customers'
    model = User
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('costumer_edit', kwargs={'costumer_id': self.object.id})


class ProductCreationView(CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'products'
    model = Product
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('product_edit', kwargs={'product_id': self.object.id})


class ProductEditView(UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'products'
    model = Product
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'product_id'

    def get_success_url(self):
        return reverse_lazy('product_edit', kwargs={'product_id': self.object.id})


class CategoryCreationView(CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'categories'
    model = ProductCategory
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('categories_overview', kwargs={'category_id': self.object.id})


class CategoryEditView(UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'categories'
    model = ProductCategory
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'category_id'

    def get_success_url(self):
        return reverse_lazy('category_edit', kwargs={'category_id': self.object.id})


class PagesOverviewView(ListView):
    template_name = 'pages/pages-overview.html'
    context_object_name = 'pages'
    model = Page


class PageCreateView(CreateView):
    template_name = 'pages/pages-create.html'
    context_object_name = 'page'
    model = Page
    fields = '__all__'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['sections'] = Section.objects.all()
        return context


class PageEditView(UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'pages'
    model = Page
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'page_id'

    def get_success_url(self):
        return reverse_lazy('page_edit', kwargs={'page_id': self.object.id})


class SectionsOverviewView(ListView):
    template_name = 'pages/sections-overview.html'
    context_object_name = 'sections'
    model = Section


class SectionCreateView(CreateView):
    from filebrowser.sites import site
    site.directory = '/var/cypetulip/uploads/'
    template_name = 'pages/sections-create.html'
    context_object_name = 'sections'
    model = Section
    fields = '__all__'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['sections'] = Section.objects.all()
        return context


class SectionEditView(UpdateView):
    from filebrowser.sites import site
    site.storage = MEDIA_ROOT
    site.directory = '/uploads/'
    template_name = 'pages/sections-create.html'
    context_object_name = 'sections'
    model = Section
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'section_id'

    def get_success_url(self):
        return reverse_lazy('section_edit', kwargs={'section_id': self.object.id})
