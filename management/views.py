from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
# Create your views here.
from django.views.generic import DetailView, ListView, View, DeleteView
from django.views.generic.edit import CreateView, UpdateView

from cms.models import Page, Section
from management.models import LdapSetting, MailSetting, LegalSetting
from permissions.models import AppUrlPermission
from permissions.permissions import check_serve_perms
from shop.models import Contact, Order, OrderItem, Product, ProductCategory, Company, Employee, OrderDetail
from shop.my_account.views import SearchOrders
from shop.order.utils import get_orderitems_once_only
from shop.utils import json_response
from utils.views import CreateUpdateView


class ManagementView(View):
    template_name = 'management.html'

    def get(self, request):
        contact = Contact.objects.filter(user=request.user)
        mail_settings = MailSetting.objects.all()
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
        if not request.user.is_staff:
            contact = Contact.objects.get(user=request.user)
        else:
            contact = {}
        _orders, search = SearchOrders.filter_orders(request, True)
        employees = Employee.objects.all()
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
                      {'orders': _orders, 'contact': contact, 'search': search, 'employees': employees})

    @check_serve_perms
    def post(self, request):
        pass


class ManagementOrderDetailView(DetailView):
    template_name = 'order-details.html'
    slug_url_kwarg = 'order'
    slug_field = 'order_hash'

    @check_serve_perms
    def get(self, request, order):
        employees = Employee.objects.all()
        if not request.user.is_staff:
            contact = Contact.objects.get(user=request.user)
            company = contact.company
        else:
            contact = {}
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
                           'order_items': order_items, 'employees': employees,
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
    model = MailSetting
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('mail_settings_details', kwargs={'mail_settings_id': self.object.id})


class LdapSettingsDetailView(CreateUpdateView):
    template_name = 'settings-details.html'
    ldap_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'ldap_settings_id'
    model = LdapSetting
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('ldap_settings_details', kwargs={'ldap_settings_id': self.object.id})


class LegalSettingsDetailView(CreateUpdateView):
    template_name = 'settings-details.html'
    ldap_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'legal_settings_id'
    model = LegalSetting
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('legal_settings_details', kwargs={'legal_settings_id': self.object.id})


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
    template_name = 'customers-overview.html'
    context_object_name = 'customers'
    model = Contact


class PermissionsOverviewView(ListView):
    template_name = 'customers-overview.html'
    context_object_name = 'permissions'
    model = AppUrlPermission


class EmployeeOverviewView(ListView):
    template_name = 'employee-overview.html'
    context_object_name = 'employees'
    model = Employee


class EmployeeCreationView(CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'employee'
    model = Employee
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('employee_overview')


class ContactEditView(UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'contact'
    model = Contact
    fields = '__all__'

    customer_id = None
    slug_field = 'id'
    slug_url_kwarg = 'contact_id'

    def get_success_url(self):
        return reverse_lazy('customers_overview')


class CompanyEditView(UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'company'
    model = Company
    fields = '__all__'

    customer_id = None
    slug_field = 'id'
    slug_url_kwarg = 'company_id'

    def get_success_url(self):
        return reverse_lazy('customers_overview')


class ProductCreationView(CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'products'
    model = Product
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('products_overview')


class ProductEditView(UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'products'
    model = Product
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'product_id'

    def get_success_url(self):
        return reverse_lazy('products_overview')


class ProductDeleteView(DeleteView):
    model = Product
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('products_overview')


class CategoryCreationView(CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'categories'
    model = ProductCategory
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('categories_overview')


class CategoryEditView(UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'categories'
    model = ProductCategory
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'category_id'

    def get_success_url(self):
        return reverse_lazy('categories_overview')


class CategoryDeleteView(DeleteView):
    model = ProductCategory
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('categories_overview')


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

    def get_success_url(self):
        return reverse_lazy('pages')


class PageEditView(UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'pages'
    model = Page
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'page_id'

    def get_success_url(self):
        return reverse_lazy('pages')


class PageDeleteView(DeleteView):
    model = Page
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('pages')


class SectionsOverviewView(ListView):
    template_name = 'pages/sections-overview.html'
    context_object_name = 'sections'
    model = Section


class SectionCreateView(CreateView):
    template_name = 'pages/sections-create.html'
    context_object_name = 'sections'
    model = Section
    fields = '__all__'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['sections'] = Section.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy('sections')


class SectionEditView(UpdateView):
    template_name = 'pages/sections-create.html'
    context_object_name = 'sections'
    model = Section
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'section_id'

    def get_success_url(self):
        return reverse_lazy('sections')


class SectionDeleteView(DeleteView):
    model = Section
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('sections')


class OrderAssignEmployeeView(View):
    def post(self, request, order_hash):
        _order = OrderDetail.objects.get(order_number=order_hash)
        _employee = Employee.objects.get(id=request.POST['id'])
        _order.assigned_employee = _employee
        if _order.state.initial:
            _order.state = _order.state.next_state
        try:
            _order.save()
            return json_response(200, x={})
        except:
            return json_response(500, x={})


class OrderCancelView(View):
    def post(self, request, order_hash):
        _order = OrderDetail.objects.get(order_number=order_hash)
        employee = Employee.objects.get(user=request.user)
        _order.assigned_employee = employee
        _order.state = _order.state.cancel_order_state
        try:
            _order.save()
            return redirect(reverse("management_detail_order", args=[order_hash]))
        except:
            return json_response(500, x={})
