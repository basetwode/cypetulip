import json

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
# Create your views here.
from django.views.generic import DetailView, ListView, View, DeleteView
from django.views.generic.edit import CreateView, UpdateView

from billing.utils import calculate_sum
from cms.mixins import LoginRequiredMixin, PermissionPostGetRequiredMixin
from cms.models import Page, Section
from management.models import LdapSetting, MailSetting, LegalSetting
from payment.models import PaymentDetail, Payment
from shipping.models import Shipment
from shop.filters import OrderDetailFilter, ProductFilter, ContactFilter, ProductCategoryFilter, SectionFilter, \
    PageFilter, ShipmentPackageFilter, FileSubItemFilter
from shop.models import Contact, Order, OrderItem, Product, ProductCategory, Company, Employee, OrderDetail, OrderState, \
    FileSubItem
from shop.my_account.views import SearchOrders
from shop.order.utils import get_orderitems_once_only
from shop.utils import json_response
from utils.views import CreateUpdateView


class ManagementView(LoginRequiredMixin, PermissionPostGetRequiredMixin, View):
    permission_get_required = ['management.get_company']
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


class ManagementOrderOverviewView(LoginRequiredMixin, View):
    template_name = 'orders-overview.html'

    def get(self, request, page=1, **kwargs):
        if not request.user.is_staff:
            contact = Contact.objects.get(user=request.user)
        else:
            contact = {}
        _orders, search = SearchOrders.filter_orders(request, True)
        filter = OrderDetailFilter(request.GET, queryset=OrderDetail.objects.all())
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
                      {'orders': _orders, 'contact': contact, 'search': search,
                       'employees': employees, 'filter': filter})

    def post(self, request):
        pass


class ManagementOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'order-details.html'
    slug_url_kwarg = 'order'
    slug_field = 'order_hash'

    def get(self, request, order):
        employees = Employee.objects.all()
        if not request.user.is_staff:
            contact = Contact.objects.get(user=request.user)
            company = contact.company
        else:
            contact = {}
        _order = Order.objects.get(order_hash=order)
        _payment_details = None
        _payment = None
        try:
            _payment_details = PaymentDetail.objects.get(order=_order)
            _payment = Payment.objects.get(details=_payment_details)
        except:
            pass
        _states = OrderState.objects.all()
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
                           'order_items_once_only': get_orderitems_once_only(_order), 'payment': _payment,
                           'payment_details': _payment_details, 'states': _states})

    def post(self, request):
        pass


class SettingsView(LoginRequiredMixin, View):

    def get(self, request):
        # <view logic>
        return HttpResponse('SettingsView')

    def post(self, request):
        # <view logic>
        return HttpResponse('result')


class MailSettingsDetailView(LoginRequiredMixin, CreateUpdateView):
    template_name = 'settings-details.html'
    mail_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'mail_settings_id'
    model = MailSetting
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('mail_settings_details', kwargs={'mail_settings_id': self.object.id})


class LdapSettingsDetailView(LoginRequiredMixin, CreateUpdateView):
    template_name = 'settings-details.html'
    ldap_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'ldap_settings_id'
    model = LdapSetting
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('ldap_settings_details', kwargs={'ldap_settings_id': self.object.id})


class LegalSettingsDetailView(LoginRequiredMixin, CreateUpdateView):
    template_name = 'settings-details.html'
    ldap_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'legal_settings_id'
    model = LegalSetting
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('legal_settings_details', kwargs={'legal_settings_id': self.object.id})


class CategoriesOverviewView(LoginRequiredMixin, ListView):
    template_name = 'categories-overview.html'
    context_object_name = 'categories'
    model = ProductCategory

    def get(self, request, *args, **kwargs):
        filter = ProductCategoryFilter(request.GET, queryset=ProductCategory.objects.all())
        return render(request, self.template_name,
                      {'filter': filter})


class ProductsOverviewView(LoginRequiredMixin, ListView):
    template_name = 'products-overview.html'
    context_object_name = 'products'
    model = Product

    def get(self, request, *args, **kwargs):
        filter = ProductFilter(request.GET, queryset=Product.objects.all())
        return render(request, self.template_name,
                      {'filter': filter})


class FileSubItemOverviewView(LoginRequiredMixin, ListView):
    template_name = 'filesubitems-overview.html'
    context_object_name = 'filesubitem'
    model = FileSubItem

    def get(self, request, *args, **kwargs):
        filter = FileSubItemFilter(request.GET, queryset=FileSubItem.objects.all())
        return render(request, self.template_name,
                      {'filter': filter})


class CustomersOverviewView(LoginRequiredMixin, ListView):
    template_name = 'customers-overview.html'
    context_object_name = 'customers'
    model = Contact

    def get(self, request, *args, **kwargs):
        filter = ContactFilter(request.GET, queryset=Contact.objects.all())
        return render(request, self.template_name,
                      {'filter': filter})


class EmployeeOverviewView(LoginRequiredMixin, ListView):
    template_name = 'employee-overview.html'
    context_object_name = 'employees'
    model = Employee


class EmployeeCreationView(LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'employee'
    model = Employee
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('employee_overview')


class ContactEditView(LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'contact'
    model = Contact
    fields = '__all__'

    customer_id = None
    slug_field = 'id'
    slug_url_kwarg = 'contact_id'

    def get_success_url(self):
        return reverse_lazy('customers_overview')


class CompanyEditView(LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'company'
    model = Company
    fields = '__all__'

    customer_id = None
    slug_field = 'id'
    slug_url_kwarg = 'company_id'

    def get_success_url(self):
        return reverse_lazy('customers_overview')


class ProductCreationView(LoginRequiredMixin, CreateView):
    template_name = 'vue/product-create-vue.html'
    context_object_name = 'products'
    model = Product
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('products_overview')

    # def get_context_data(self, **kwargs):
    #     context_data = super(ProductCreationView, self).get_context_data()
    #     context_data['product_attribute_types'] = json.dumps(ProductAttributeType.objects.all().values())
    #     return context_data


class ProductEditView(LoginRequiredMixin, UpdateView):
    template_name = 'vue/product-create-vue.html'
    context_object_name = 'products'
    model = Product
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'product_id'

    def get_success_url(self):
        return reverse_lazy('products_overview')


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('products_overview')


class FileSubItemCreationView(LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'filesubitem'
    model = FileSubItem
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('filesubitem_overview')


class FileSubItemEditView(LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'filesubitem'
    model = FileSubItem
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'filesubitem_id'

    def get_success_url(self):
        return reverse_lazy('filesubitem_overview')


class FileSubItemDeleteView(LoginRequiredMixin, DeleteView):
    model = FileSubItem
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('filesubitem_overview')


class CategoryCreationView(LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'categories'
    model = ProductCategory
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('categories_overview')


class CategoryEditView(LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'categories'
    model = ProductCategory
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'category_id'

    def get_success_url(self):
        return reverse_lazy('categories_overview')


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductCategory
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('categories_overview')


class PagesOverviewView(LoginRequiredMixin, ListView):
    template_name = 'pages/pages-overview.html'
    context_object_name = 'pages'
    model = Page

    def get(self, request, *args, **kwargs):
        filter = PageFilter(request.GET, queryset=Page.objects.all())
        return render(request, self.template_name,
                      {'filter': filter})


class PageCreateView(LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'page'
    model = Page
    fields = '__all__'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['sections'] = Section.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy('pages')


class PageEditView(LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'pages'
    model = Page
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'page_id'

    def get_success_url(self):
        return reverse_lazy('pages')


class PageDeleteView(LoginRequiredMixin, DeleteView):
    model = Page
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('pages')


class SectionsOverviewView(LoginRequiredMixin, ListView):
    template_name = 'pages/sections-overview.html'
    context_object_name = 'sections'
    model = Section

    def get(self, request, *args, **kwargs):
        filter = SectionFilter(request.GET, queryset=Section.objects.all())
        return render(request, self.template_name,
                      {'filter': filter})


class SectionCreateView(LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'sections'
    model = Section
    fields = '__all__'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['sections'] = Section.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy('sections')


class SectionEditView(LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'sections'
    model = Section
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'section_id'

    def get_success_url(self):
        return reverse_lazy('sections')


class SectionDeleteView(LoginRequiredMixin, DeleteView):
    model = Section
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('sections')


class OrderAssignEmployeeView(LoginRequiredMixin, View):
    def post(self, request, order_hash):
        _order = OrderDetail.objects.get(order_number=order_hash)
        _employee = Employee.objects.get(id=request.POST['id'])
        _order.assigned_employee = _employee
        try:
            _order.save()
            return json_response(200, x={})
        except:
            return json_response(500, x={})


class AccountingView(LoginRequiredMixin, View):
    model = Order
    template_name = "accounting-dashboard.html"

    def get(self, request):
        total_netto = OrderItem.objects.aggregate(Sum('price'))
        open_order_state_id = OrderState.objects.get(initial=True).id
        all_order_items = OrderItem.objects.filter()
        total_brutto = calculate_sum(all_order_items, True)
        last_orders = OrderDetail.objects.all()[:5]
        _open_orders_state = []
        for order in OrderDetail.objects.all():
            if not OrderState.last_state(order.state):
                _open_orders_state.append(order)
        counted_open_orders = len(_open_orders_state)
        counted_open_shipments = OrderDetail.objects.filter(order__is_send=False).count()
        counted_open_payments = Payment.objects.filter(is_paid=False).count()

        return render(request, self.template_name,
                      {'total_netto': total_netto, 'total_brutto': total_brutto,
                       'counted_open_orders': counted_open_orders,
                       'counted_open_payments': counted_open_payments, 'counted_open_shipments': counted_open_shipments,
                       'last_orders': last_orders, 'open_order_state_id': open_order_state_id})


class OrderPayView(View):
    def post(self, request, order_hash):
        _order = Order.objects.get(order_hash=order_hash)
        _payment_detail = PaymentDetail.objects.get(order=_order)
        _payment = Payment.objects.get(details=_payment_detail)
        _payment.is_paid = True
        try:
            _payment.save()
            return redirect(request.META.get('HTTP_REFERER'))
        except:
            return json_response(500, x={})


class OrderShipView(View):
    def post(self, request, order_hash):
        _order = Order.objects.get(order_hash=order_hash)
        _order.is_send = True
        try:
            _order.save()
            return redirect(request.META.get('HTTP_REFERER'))
        except:
            return json_response(500, x={})


class OrderChangeStateView(View):
    def post(self, request, order_hash):
        _order = OrderDetail.objects.get(order_number=order_hash)
        _next_state = OrderState.objects.get(id=request.POST['id'])
        _order.state = _next_state
        try:
            _order.save()
            return redirect(request.META.get('HTTP_REFERER'))
        except:
            return json_response(500, x={})


class ShipmentOverviewView(LoginRequiredMixin, ListView):
    template_name = 'shipment-overview.html'
    context_object_name = 'shipment'
    model = Shipment

    def get(self, request, *args, **kwargs):
        filter = ShipmentPackageFilter(request.GET, queryset=Shipment.objects.all())
        return render(request, self.template_name,
                      {'filter': filter})


