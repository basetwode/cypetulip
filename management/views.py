import csv
import secrets
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sessions.models import Session
from django.core import management
from django.core.files import File
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
# Create your views here.
from django.views.generic import DetailView, ListView, View, DeleteView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django_filters.views import FilterView

from billing.utils import calculate_sum
from billing.views import GeneratePDFFile
from cms.models import Page, Section
from management.filters import OrderDetailFilter
from management.forms import OrderDetailForm, OrderForm, OrderItemForm, PaymentProviderForm, ProductForm, \
    ContactUserForm, ContactUserIncludingPasswordForm, ContactUserUpdatePasswordForm, MergeAccountsForm, ClearCacheForm, \
    CustomerImportForm
from management.mixins import NotifyNewCustomerAccountView
from management.models import LdapSetting, MailSetting, LegalSetting, ShopSetting, Header, Footer, CacheSetting
from payment.models import PaymentDetail, Payment, PaymentMethod, PAYMENTMETHOD_BILL_NAME, PaymentProvider
from permissions.mixins import LoginRequiredMixin
from shipping.models import Shipment
from shop.filters import ProductFilter, ContactFilter, ProductCategoryFilter, SectionFilter, \
    PageFilter, FooterFilter, HeaderFilter, ProductSubItemFilter, ShipmentFilter
from shop.mixins import WizardView, RepeatableWizardView
from shop.models import Contact, Order, OrderItem, Product, ProductCategory, Company, Employee, OrderDetail, OrderState, \
    FileSubItem, IndividualOffer, ProductSubItem, NumberSubItem, CheckBoxSubItem, SelectSubItem, SelectItem, Address, \
    Discount, PercentageDiscount, FixedAmountDiscount
from shop.order.utils import get_orderitems_once_only
from shop.utils import json_response
from utils.mixins import EmailMixin, PaginatedFilterViews
from utils.views import CreateUpdateView


class ManagementView(LoginRequiredMixin, TemplateView):
    permission_get_required = ['management.view_management']
    template_name = 'management.html'

    def get_context_data(self, **kwargs):
        contact = Contact.objects.filter(user_ptr=self.request.user)
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        user_id_list = [data.get_decoded().get('_auth_user_id', None) for data in active_sessions]
        users = User.objects.filter(id__in=user_id_list)

        return {**super(ManagementView, self).get_context_data(), **{'contact': contact, 'users': users,
                                                                     'active_sessions': Session.objects.filter(
                                                                         expire_date__gte=timezone.now())}}


class ManagementOrderOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    model = OrderDetail
    template_name = 'orders-overview.html'
    paginate_by = 20
    filterset_class = OrderDetailFilter

    def get_queryset(self):
        return super(ManagementOrderOverviewView, self).get_queryset().filter(state__isnull=False) \
            .order_by('-date_added')


class ManagementOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'order-details.html'
    model = Order
    slug_url_kwarg = 'order'
    slug_field = 'order_hash'

    def get_context_data(self, **kwargs):
        employees = Employee.objects.all()
        _order_detail = OrderDetail.objects.get(order=self.object.order_id)
        _payment_details = None
        _payment = None
        try:
            _payment_details = PaymentDetail.objects.get(order=self.object)
            _payment = Payment.objects.get(details=_payment_details)
        except:
            pass
        _states = OrderState.objects.all()
        order_items = OrderItem.objects.filter(order=self.object, order_item__isnull=True,
                                               product__in=Product.objects.all())

        total = calculate_sum(order_items)
        return {**super(ManagementOrderDetailView, self).get_context_data(**kwargs), **
        {'order_details': _order_detail, 'order': self.object, 'contact': _order_detail.contact, 'total': total,
         'order_items': order_items, 'employees': employees,
         'order_items_once_only': get_orderitems_once_only(self.object), 'payment': _payment,
         'payment_details': _payment_details, 'states': _states}}


class MailSettingsDetailView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'settings-details.html'
    mail_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'mail_settings_id'
    model = MailSetting
    fields = '__all__'
    success_message = _("Mailsettings updated successfully")

    def get_success_url(self):
        return reverse_lazy('mail_settings_details', kwargs={'mail_settings_id': self.object.id})


class ShopSettingsDetailView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'settings-details.html'
    shop_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'shop_settings_id'
    model = ShopSetting
    fields = '__all__'
    success_message = _("Shopsettings updated successfully")

    def get_success_url(self):
        return reverse_lazy('shop_settings_details', kwargs={'shop_settings_id': self.object.id})


class LdapSettingsDetailView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'settings-details.html'
    ldap_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'ldap_settings_id'
    model = LdapSetting
    fields = '__all__'
    success_message = _("Ldapsettings updated successfully")

    def get_success_url(self):
        return reverse_lazy('ldap_settings_details', kwargs={'ldap_settings_id': self.object.id})


class LegalSettingsDetailView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'settings-details.html'
    ldap_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'legal_settings_id'
    model = LegalSetting
    fields = '__all__'
    success_message = _("Ldapsettings updated successfully")

    def get_success_url(self):
        return reverse_lazy('legal_settings_details', kwargs={'legal_settings_id': self.object.id})


class CategoriesOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'categories-overview.html'
    context_object_name = 'categories'
    model = ProductCategory
    filterset_class = ProductCategoryFilter


class ProductsOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'products-overview.html'
    context_object_name = 'products'
    model = Product
    paginate_by = 40
    ordering = 'id'
    filterset_class = ProductFilter


class SubItemOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'subitems-overview.html'
    context_object_name = 'filesubitem'
    paginate_by = 40
    model = ProductSubItem
    filterset_class = ProductSubItemFilter

    def get_queryset(self):
        return super(SubItemOverviewView, self).get_queryset().filter(product=None)


class CustomersOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'customers-overview.html'
    model = Contact
    paginate_by = 20
    ordering = ['company__customer_nr', 'company_customer_nr']
    filterset_class = ContactFilter


class EmployeeOverviewView(LoginRequiredMixin, ListView):
    template_name = 'employee-overview.html'
    context_object_name = 'employees'
    model = Employee


class EmployeeCreationView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'employee'
    model = Employee
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('employee_overview')


class ProductCreationView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'vue/product-create-vue.html'
    context_object_name = 'products'
    model = Product
    form_class = ProductForm
    success_message = _("Product created successfully")

    def get_success_url(self):
        return reverse_lazy('product_edit', kwargs={'product_id': self.object.id})


class ProductEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'vue/product-create-vue.html'
    context_object_name = 'products'
    form_class = ProductForm
    model = Product
    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'product_id'
    success_message = _("Product updated successfully")

    def get_success_url(self):
        return reverse_lazy('product_edit', kwargs={'product_id': self.object.id})


class ProductDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Product
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Product deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('products_overview')


class CheckboxSubItemCreateUpdateView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'generic-create.html'
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'subitem_id'
    model = CheckBoxSubItem
    fields = ['price', 'tax', 'price_on_request', 'name', 'description', 'details',
              'is_required', 'is_multiple_per_item', 'is_once_per_order'
              ]
    success_message = _("Subitem updated successfully")

    def get_success_url(self):
        return reverse_lazy('checkboxsubitem_create', kwargs={'subitem_id': self.object.id})


class NumberSubItemCreateUpdateView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'generic-create.html'
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'subitem_id'
    model = NumberSubItem
    fields = ['price', 'tax', 'price_on_request', 'name', 'description', 'details',
              'is_required', 'is_multiple_per_item', 'is_once_per_order'
              ]
    success_message = _("Subitem updated successfully")

    def get_success_url(self):
        return reverse_lazy('numbersubitem_create', kwargs={'subitem_id': self.object.id})


class FileSubItemCreationView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'generic-create.html'
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'subitem_id'
    model = FileSubItem
    fields = ['price', 'tax', 'price_on_request', 'name', 'description', 'details',
              'is_required', 'is_multiple_per_item', 'is_once_per_order',
              'extensions']
    success_message = _("Subitem updated successfully")

    def get_success_url(self):
        return reverse_lazy('filesubitem_create', kwargs={'subitem_id': self.object.id})


class SelectSubItemCreationView(SuccessMessageMixin, LoginRequiredMixin, WizardView):
    page_title = _('Create Selectsubitem')
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'subitem_id'
    model = SelectSubItem
    fields = ['price', 'tax', 'price_on_request', 'name', 'description', 'details',
              'is_required', 'is_multiple_per_item', 'is_once_per_order',
              ]
    success_message = _("Subitem updated successfully")

    def get_success_url(self):
        return reverse_lazy('selectsubitem_create', kwargs={'subitem_id': self.object.id})


class SelectItemCreationView(SuccessMessageMixin, LoginRequiredMixin, RepeatableWizardView):
    page_title = _('Create new select item')
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'subitem_id'
    model = SelectItem
    fields = ['name', 'price', 'tax']
    pk_url_kwarg = 'id'
    parent_key = 'select'
    self_url = 'selectitem_create'
    delete_url = 'selectitem_delete'
    success_message = _("Selectitem updated successfully")

    def get_back_url(self):
        return reverse_lazy('selectsubitem_create', kwargs={'subitem_id': self.get_parent_id()})

    def get_next_url(self):
        return reverse_lazy('subitem_overview')

    def get_success_url(self):
        return reverse_lazy('selectitem_create', kwargs={'id': '', 'parent_id': self.get_parent_id()})

    def form_valid(self, form):
        selectitem = form.save(commit=False)
        selectitem.select = SelectSubItem.objects.get(id=self.get_parent_id())
        return super(SelectItemCreationView, self).form_valid(form)


class SelectItemDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = SelectItem
    slug_field = 'id'
    pk_url_kwarg = 'id'
    template = ''
    success_message = _("Select Item deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('subitem_overview')


class SubItemDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = ProductSubItem
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Subitem deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('subitem_overview')


class CategoryCreationView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'categories'
    model = ProductCategory
    fields = '__all__'
    success_message = _("Category created successfully")

    def get_success_url(self):
        return reverse_lazy('category_edit', kwargs={'category_id': self.object.id})


class CategoryEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'categories'
    model = ProductCategory
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'category_id'
    success_message = _("Category updated successfully")

    def get_success_url(self):
        return reverse_lazy('category_edit', kwargs={'category_id': self.object.id})


class CategoryDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = ProductCategory
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Category deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('categories_overview')


class PagesOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'pages/pages-overview.html'
    context_object_name = 'pages'
    model = Page
    filterset_class = PageFilter


class PageCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'page'
    model = Page
    fields = '__all__'
    success_message = _("Page created successfully")

    def get_success_url(self):
        return reverse_lazy('page_edit', kwargs={'page_id': self.object.id})


class PageEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'pages'
    model = Page
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'page_id'
    success_message = _("Page updated successfully")

    def get_success_url(self):
        return reverse_lazy('page_edit', kwargs={'page_id': self.object.id})


class PageDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Page
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Page deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('pages')


class SectionsOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'pages/sections-overview.html'
    context_object_name = 'sections'
    model = Section
    filterset_class = SectionFilter


class SectionCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'sections'
    model = Section
    fields = '__all__'
    success_message = _("Section created successfully")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['sections'] = Section.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy('section_edit', kwargs={'section_id': self.object.id})


class SectionEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'sections'
    model = Section
    fields = '__all__'
    success_message = _("Section updated successfully")

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'section_id'

    def get_success_url(self):
        return reverse_lazy('section_edit', kwargs={'section_id': self.object.id})


class SectionDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Section
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Section deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
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


class OrderPayView(View):
    def post(self, request, order_hash):
        _order = Order.objects.get(order_hash=order_hash)
        _payment_detail = PaymentDetail.objects.get(order=_order)
        _payment = Payment.objects.get(details=_payment_detail)
        _payment.is_paid = True
        _order_detail = OrderDetail.objects.get(order_number=order_hash)
        _order_detail.state = OrderState.objects.get(is_paid_state=True)
        _order_detail.save()
        try:
            _payment.save()
            messages.success(request, _("Order saved"))
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


class OrderAcceptInvoiceView(View, EmailMixin):
    email_template = 'mail/order_accepted_invoice.html'

    def post(self, request, order_hash):
        _order = OrderDetail.objects.get(order_number=order_hash)

        if _order.state.initial:
            _order.state = _order.state.next_state
            _order.assigned_employee = Employee.objects.get(user=request.user)
        if not _order.date_bill:
            _order.date_bill = datetime.now()
            _order.assigned_employee = Employee.objects.get(user=request.user)
        _order.bill_sent = True
        _order.save()
        try:
            self.send_invoice(_order)
            _order.save()
            messages.success(request, _("Invoice sent"))
            return redirect(request.META.get('HTTP_REFERER'))
        except Exception as e:
            messages.error(request, _("Something went wrong"))
            return redirect(request.META.get('HTTP_REFERER'))

    def send_invoice(self, _order, ):
        if not _order.bill_number:
            _order.bill_number = (OrderDetail.objects.filter(bill_number__isnull=False).order_by(
                'bill_number').last().bill_number + 1) \
                if OrderDetail.objects.filter(bill_number__isnull=False).exists() else 1
            _order.save()
        pdf = GeneratePDFFile().generate(_order.order)
        _order.bill_file = File(pdf, f"I_{_order.unique_bill_nr()}.pdf")
        _order.save()
        total = calculate_sum(_order.order.orderitem_set, True)
        self.send_mail(_order.contact, _('Your Invoice ') + _order.unique_bill_nr(), '',
                       {'object': _order.order,
                        'contact': _order.contact,
                        'total': total,
                        'order': _order.order,
                        'order_detail': _order,
                        'files': {_(
                            'Invoice') + "_" + _order.unique_bill_nr() +
                                  ".pdf": pdf.getvalue()},
                        'host': self.request.META[
                            'HTTP_HOST']},
                       _order.contact.billing_mail)


class ShipmentOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'shipment-overview.html'
    context_object_name = 'shipment'
    model = Shipment
    filterset_class = ShipmentFilter


class IndividualOfferRequestOverview(LoginRequiredMixin, ListView):
    template_name = 'individualoffers-overview.html'
    model = IndividualOffer
    paginate_by = 50
    ordering = ['-date_added']


class IndividualOfferRequestView(LoginRequiredMixin, DetailView):
    template_name = 'individualoffer.html'
    model = IndividualOffer
    context_object_name = 'offer'
    slug_url_kwarg = 'offer_id'
    pk_url_kwarg = 'offer_id'


class DeleteIndividualOfferRequest(LoginRequiredMixin, DeleteView):
    model = IndividualOffer
    success_url = reverse_lazy('individualoffers_overview')
    pk_url_kwarg = 'offer_id'

    def get_success_url(self):
        messages.success(self.request, _('Individual offer request deleted'))
        return super().get_success_url()


class DeleteOrder(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'generic-create-form.html'
    slug_url_kwarg = 'order_hash'
    slug_field = 'order_hash'

    def get_success_url(self):
        messages.success(self.request, _('Order deleted'))
        return reverse_lazy('management_all_orders')

    def delete(self, request, *args, **kwargs):
        Shipment.objects.filter(order=self.get_object().orderdetail_set.first()).delete()
        return super(DeleteOrder, self).delete(request, *args, **kwargs)


class CreateOrderView(SuccessMessageMixin, LoginRequiredMixin, WizardView):
    page_title = _('Select customer')
    template_name = 'generic-create-form.html'
    order_id = None
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = Order
    form_class = OrderForm
    success_message = _('Order created successfully')

    def get_initial(self):
        initial = super(CreateOrderView, self).get_initial()
        if 'contact' in self.request.GET and self.request.GET['contact']:
            initial['company'] = Contact.objects.get(id=self.request.GET['contact']).company.id
        return initial

    def form_valid(self, form):
        order = form.save(commit=False)
        if 'ior' in self.request.GET and self.request.GET['ior']:
            order.individual_offer_request = IndividualOffer.objects.get(id=self.request.GET['ior'])
        return super(CreateOrderView, self).form_valid(form)

    def get_back_url(self):
        if self.get_object():
            return reverse_lazy('management_detail_order',
                                kwargs={'order': self.get_object().order_hash})
        else:
            return reverse_lazy('individualoffers_overview')

    def get_success_url(self):
        order_detail, created = OrderDetail.objects.get_or_create(order=self.object,
                                                                  order_number=self.object.order_hash)
        if not order_detail.state:
            order_detail.state = OrderState.objects.get(initial=True)
            order_detail.save()
        return reverse_lazy('create_order_detail', kwargs={'parent_id': self.object.id, 'id': order_detail.id})


class CreateOrderDetailView(SuccessMessageMixin, LoginRequiredMixin, WizardView):
    page_title = _('Define order details')
    model = OrderDetail
    pk_url_kwarg = 'id'
    form_class = OrderDetailForm

    def get_back_url(self):
        return reverse_lazy('create_order', kwargs={'id': self.get_parent_id()})

    def get_success_url(self):
        return reverse_lazy('create_order_item', kwargs={'id': '', 'parent_id': self.get_object().id})

    def form_valid(self, form):
        order_detail = form.save(commit=False)
        if order_detail.state is None:
            order_detail.state = OrderState.objects.get(initial=True)
        form.save()
        if order_detail.order.paymentdetail_set.count() == 0:
            payment_detail = PaymentDetail(order=order_detail.order,
                                           method=PaymentMethod.objects.get(name=PAYMENTMETHOD_BILL_NAME),
                                           user=order_detail.contact)
            payment_detail.save()
            payment = Payment(details=payment_detail, is_paid=False)
            payment.save()

        return super(CreateOrderDetailView, self).form_valid(form)

    def get_form_kwargs(self):
        form_kwargs = super(CreateOrderDetailView, self).get_form_kwargs()
        return {**form_kwargs, **{'contacts': Contact.objects.filter(company=self.object.order.company)}}


class CreateOrderSubItem(LoginRequiredMixin, WizardView):
    page_title = _('Configure products')
    template_name = 'order-item-create.html'
    pk_url_kwarg = 'id'
    parent_key = 'order_detail'
    self_url = 'create_order_item'
    model = OrderItem
    fields = []

    def get_back_url(self):
        return reverse_lazy('create_order_item', kwargs={'id': '',
                                                         'parent_id': OrderDetail.objects.get(
                                                             id=self.get_parent_id()).id})

    def get_success_url(self):
        return reverse_lazy('management_detail_order',
                            kwargs={'order': OrderDetail.objects.get(id=self.get_parent_id()).order.order_hash})

    def get_context_data(self, **kwargs):
        return {**super(CreateOrderSubItem, self).get_context_data(**kwargs),
                **{'order_details': OrderDetail.objects.get(id=self.get_parent_id()).order,
                   'success_url': self.get_success_url()}}


class CreateOrderItem(LoginRequiredMixin, RepeatableWizardView):
    page_title = _('Select products')
    form_class = OrderItemForm
    model = OrderItem
    pk_url_kwarg = 'id'
    parent_key = 'order_detail'
    self_url = 'create_order_item'
    delete_url = 'delete_order_item'

    def form_valid(self, form):
        order_item = form.save(commit=False)
        order_item.order_detail = OrderDetail.objects.get(id=self.get_parent_id())
        order_item.order = Order.objects.get(id=order_item.order_detail.order.id)
        if hasattr(order_item.product, 'product'):
            order_item.product.product.decrease_stock()
        return super(CreateOrderItem, self).form_valid(form)

    def get_back_url(self):
        return reverse_lazy('create_order_detail', kwargs={'id': self.get_parent_id(),
                                                           'parent_id': OrderDetail.objects.get(
                                                               id=self.get_parent_id()).order.id})

    def get_next_url(self):
        return reverse_lazy('create_order_subitem',
                            kwargs={'parent_id': self.get_parent_id()})

    def get_success_url(self):
        return reverse_lazy('create_order_item', kwargs={'id': '', 'parent_id': self.get_parent_id()})

    def get_form_kwargs(self):
        form_kwargs = super(CreateOrderItem, self).get_form_kwargs()
        return {**form_kwargs, **{'order': OrderDetail.objects.get(
            id=self.get_parent_id()).order}}


class DeleteOrderItem(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = OrderItem
    template_name = 'generic-create-form.html'
    pk_url_kwarg = 'id'
    success_message = _('Order item deleted successfully')

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('create_order_item', kwargs={'id': '',
                                                         'parent_id': OrderDetail.objects.get(
                                                             id=self.kwargs['parent_id']).id})


class PaymentProviderSettings(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = 'payment-settings.html'
    form_class = PaymentProviderForm
    success_url = reverse_lazy('payment_settings_details')
    success_message = _("Payment settings saved!")

    def form_valid(self, form):
        paypal_provider = PaymentProvider.objects.get(api="PayPal")
        paypal_method = PaymentMethod.objects.get(provider=paypal_provider)
        invoice_provider = PaymentProvider.objects.get(api="Bill")
        invoice_method = PaymentMethod.objects.get(provider=invoice_provider)
        prepayment_provider = PaymentProvider.objects.get(api="Prepayment")
        prepayment_method = PaymentMethod.objects.get(provider=prepayment_provider)

        invoice_method.enabled = form.cleaned_data['invoice_enabled']
        invoice_method.details = form.cleaned_data['prepayment_description']
        prepayment_method.enabled = form.cleaned_data['prepayment_enabled']
        prepayment_method.details = form.cleaned_data['invoice_description']
        paypal_method.enabled = form.cleaned_data['paypal_enabled']
        paypal_method.details = form.cleaned_data['paypal_description']
        paypal_provider.user_name = form.cleaned_data['paypal_user']
        paypal_provider.secret = form.cleaned_data['paypal_secret']
        paypal_provider.use_sandbox = form.cleaned_data['paypal_use_sandbox']

        invoice_method.save()
        prepayment_method.save()
        paypal_method.save()
        paypal_provider.save()
        return super(PaymentProviderSettings, self).form_valid(form)

    def get_initial(self):
        initial = super(PaymentProviderSettings, self).get_initial()
        paypal_provider, created = PaymentProvider.objects.get_or_create(api="PayPal")
        paypal_method, created = PaymentMethod.objects.get_or_create(provider=paypal_provider, name="PayPal")
        invoice_provider, created = PaymentProvider.objects.get_or_create(api="Bill")
        invoice_method, created = PaymentMethod.objects.get_or_create(provider=invoice_provider, name="Bill")
        prepayment_provider, created = PaymentProvider.objects.get_or_create(api="Prepayment")
        prepayment_method, created = PaymentMethod.objects.get_or_create(provider=prepayment_provider,
                                                                         name="Prepayment")
        initial.update({'prepayment_enabled': prepayment_method.enabled,
                        'prepayment_description': prepayment_method.details,
                        'invoice_enabled': invoice_method.enabled,
                        'invoice_description': invoice_method.details,
                        'paypal_enabled': paypal_method.enabled,
                        'paypal_description': paypal_method.details,
                        'paypal_user': paypal_provider.user_name,
                        'paypal_secret': paypal_provider.secret,
                        'paypal_use_sandbox': paypal_provider.use_sandbox,
                        })
        return initial


class HeadersOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'pages/headers-overview.html'
    context_object_name = 'headers'
    model = Header
    filterset_class = HeaderFilter


class HeaderCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'header'
    model = Header
    fields = '__all__'
    success_message = _("Header created successfully")

    def get_success_url(self):
        return reverse_lazy('header_edit', kwargs={'header_id': self.object.id})


class HeaderEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'header'
    model = Header
    fields = '__all__'

    slug_field = 'id'
    slug_url_kwarg = 'header_id'
    success_message = _("Header updated successfully")

    def get_success_url(self):
        return reverse_lazy('header_edit', kwargs={'header_id': self.object.id})


class HeaderDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Header
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Header deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('headers_overview')


class FootersOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'pages/footers-overview.html'
    context_object_name = 'footers'
    model = Footer
    filterset_class = FooterFilter


class FooterCreateView(LoginRequiredMixin, CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'footer'
    model = Footer
    fields = '__all__'
    success_message = _("Footer created successfully")

    def get_success_url(self):
        return reverse_lazy('footer_edit', kwargs={'footer_id': self.object.id})


class FooterEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'footer'
    model = Footer
    fields = '__all__'

    slug_field = 'id'
    slug_url_kwarg = 'footer_id'
    success_message = _("Footer updated successfully")

    def get_success_url(self):
        return reverse_lazy('footer_edit', kwargs={'footer_id': self.object.id})


class FooterDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Footer
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Footer deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('footers_overview')


class CompanyCreationView(SuccessMessageMixin, LoginRequiredMixin, WizardView):
    page_title = _('Create Company')
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = Company
    fields = '__all__'
    success_message = _("Company created successfully")

    def get_back_url(self):
        return reverse_lazy('management_index')

    def get_success_url(self):
        return reverse_lazy('contact_create', kwargs={'id': '', 'parent_id': self.object.id})


class CompanyDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Company
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Company deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('customers_overview')


class ContactCreationView(SuccessMessageMixin, LoginRequiredMixin, RepeatableWizardView, NotifyNewCustomerAccountView):
    page_title = _('Create new contact')
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = Contact
    pk_url_kwarg = 'id'
    parent_key = 'company'
    self_url = 'contact_create'
    delete_url = 'contact_delete'
    requires_selection_on_next = True
    text_add_item = _("Add contact")
    text_select_item = _("Select a contact to edit")

    def get_back_url(self):
        return reverse_lazy('company_create', kwargs={'id': self.get_parent_id()})

    def get_next_url(self):
        return reverse_lazy('address_create', kwargs={'id': '',
                                                      'parent_id': self.get_object().id if self.get_object() else '0'})

    def get_success_url(self):
        return reverse_lazy('contact_create', kwargs={'id': '', 'parent_id': self.get_parent_id()})

    def get_form_class(self):
        if self.get_object():
            return ContactUserForm
        else:
            return ContactUserIncludingPasswordForm

    def form_valid(self, form):
        contact = form.save(commit=False)
        contact.company = Company.objects.get(id=self.get_parent_id())
        contact.username = contact.email
        contact.save()
        if 'notify_customer' in form.cleaned_data and form.cleaned_data['notify_customer']:
            self.notify_client(_("Your account at ") + LegalSetting.objects.first().company_name, contact,
                               form.cleaned_data['new_password1'])

        group = Group.objects.get(name="client")
        group.user_set.add(contact)
        if form.cleaned_data['is_client_supervisor']:
            sgroup = Group.objects.get(name='client supervisor')
            sgroup.user_set.add(contact)
        else:
            sgroup = Group.objects.get(name='client supervisor')
            sgroup.user_set.remove(contact)

        return super(ContactCreationView, self).form_valid(form)

    def get_initial(self):
        initial = super(ContactCreationView, self).get_initial()
        initial['is_client_supervisor'] = self.object.groups.filter(name='client supervisor').exists() \
            if self.object else False
        initial['notify_customer'] = False if self.object else True
        gen_password = secrets.token_urlsafe(10)
        initial['new_password1'] = gen_password
        initial['new_password2'] = gen_password
        return initial


class ContactResetPwdView(SuccessMessageMixin, LoginRequiredMixin, UpdateView, NotifyNewCustomerAccountView):
    template_name = 'generic-edit.html'
    model = Contact
    form_class = ContactUserUpdatePasswordForm
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse_lazy('customers_overview')

    def get_initial(self):
        initial = super(ContactResetPwdView, self).get_initial()
        initial['notify_customer'] = True
        gen_password = secrets.token_urlsafe(10)
        initial['new_password1'] = gen_password
        initial['new_password2'] = gen_password
        return initial

    def form_valid(self, form):
        if 'notify_customer' in form.cleaned_data and form.cleaned_data['notify_customer']:
            self.notify_client(_("Your account at ") + LegalSetting.objects.first().company_name, self.get_object(),
                               form.cleaned_data['new_password1'])
        return super(ContactResetPwdView, self).form_valid(form)


class ContactDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Contact
    slug_field = 'id'
    pk_url_kwarg = 'id'
    template = ''
    success_message = _("Contact deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)

        return reverse_lazy('contact_create')


class AddressCreationView(SuccessMessageMixin, LoginRequiredMixin, RepeatableWizardView):
    page_title = _('Create new address')
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = Address
    fields = ['name', 'street', 'number', 'zipcode', 'city']
    pk_url_kwarg = 'id'
    parent_key = 'contact'
    self_url = 'address_create'
    delete_url = 'address_delete'
    text_add_item = _("Add address")
    text_select_item = _("Select an address to edit")

    def get_back_url(self):
        return reverse_lazy('contact_create', kwargs={'id': Contact.objects.get(id=self.get_parent_id()).id,
                                                      'parent_id': Contact.objects.get(
                                                          id=self.get_parent_id()).company.id})

    def get_next_url(self):
        return reverse_lazy('management_index')

    def get_success_url(self):
        return reverse_lazy('address_create', kwargs={'id': '', 'parent_id': self.get_parent_id()})

    def form_valid(self, form):
        address = form.save(commit=False)
        address.contact = Contact.objects.get(id=self.get_parent_id())
        address.save()
        return super(AddressCreationView, self).form_valid(form)


class AddressDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Address
    slug_field = 'id'
    pk_url_kwarg = 'id'
    template = ''
    success_message = _("Address deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('address_create')


class PercentageDiscountEditView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'generic-edit.html'
    model = PercentageDiscount
    fields = '__all__'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    success_message = _("Discount updated successfully")

    def get_success_url(self):
        return reverse_lazy('percentage_discount_edit', kwargs={'id': self.object.id})


class FixedAmountDiscountEditView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'generic-edit.html'
    model = FixedAmountDiscount
    fields = '__all__'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    success_message = _("Discount updated successfully")

    def get_success_url(self):
        return reverse_lazy('fixed_discount_edit', kwargs={'id': self.object.id})


class DiscountOverview(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'discount-overview.html'
    model = Discount
    paginate_by = 50
    ordering = ['-date_added']


class MergeAccounts(SuccessMessageMixin, LoginRequiredMixin, FormView, NotifyNewCustomerAccountView):
    form_class = MergeAccountsForm
    template_name = 'generic-edit.html'
    success_url = reverse_lazy('customers_overview')

    def form_valid(self, form):
        contacts_to_merge = form.cleaned_data['contacts']
        contact_to_merge_to = form.cleaned_data['leading_contact']

        companies = Company.objects.filter(contact__in=contacts_to_merge)
        orders = Order.objects.filter(company__in=companies)
        order_details = OrderDetail.objects.filter(contact__in=contacts_to_merge)
        addresses = Address.objects.filter(contact__in=contacts_to_merge)

        orders.update(company=contact_to_merge_to.company, session="")
        order_details.update(contact=contact_to_merge_to)
        addresses.update(contact=contact_to_merge_to)
        # todo: merge addresses to remove dups
        contacts_to_merge.delete()
        companies.delete()

        messages.success(self.request, _("Merge done") + " | " +
                         str(contacts_to_merge.count()) + "Accounts, " + str(order_details.count()) + "orders")

        if not contact_to_merge_to.is_registered():
            contact_to_merge_to.username = contact_to_merge_to.email
            password = secrets.token_urlsafe(10)
            contact_to_merge_to.set_password(password)
            contact_to_merge_to.save()
            self.notify_client(_("Your account at ") + LegalSetting.objects.first().company_name, contact_to_merge_to,
                               password)

            group = Group.objects.get(name="client")
            group.user_set.add(contact_to_merge_to)
            sgroup = Group.objects.get(name='client supervisor')
            sgroup.user_set.add(contact_to_merge_to)

        return super(MergeAccounts, self).form_valid(form)

    def get_initial(self):
        initial = super(MergeAccounts, self).get_initial()
        initial['notify_customer'] = True
        return initial

    def get_form_kwargs(self):
        form_kwargs = super(MergeAccounts, self).get_form_kwargs()
        return {**form_kwargs, **{'contact': Contact.objects.get(id=self.kwargs['id'])}}


class OrderCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    model = Order
    slug_field = 'order_hash'
    slug_url_kwarg = 'order_hash'
    template_name = 'vue/order-create-vue.html'
    fields = '__all__'
    context_object_name = 'order'
    success_message = _('Order created successfully')


class CacheManagementView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = 'cache-management.html'
    form_class = ClearCacheForm
    success_url = reverse_lazy('cache_management_view')

    def form_valid(self, form):
        form_valid = super(CacheManagementView, self).form_valid(form)
        if form.cleaned_data['clear_html_cache']:
            self.flush_cache()
            messages.success(self.request, _("HTML Cache cleared successfully"))
        if form.cleaned_data['recompile_css_js']:
            try:
                management.call_command('collectstatic', verbosity=0, interactive=False)
                management.call_command('compress', verbosity=0)
                messages.success(self.request, _("JS/CSS successfully recompiled"))
            except:
                messages.error(self.request, _("Offline compression not enabled. CSS/JS are generated on-the-fly"))

            cache_setting = CacheSetting.objects.first()
            cache_setting.cache_clear_required = False
            cache_setting.save()
        return form_valid

    def flush_cache(self):
        from django.core.cache import cache
        cache.clear()


class CustomerImportView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = 'customer-import.html'
    form_class = CustomerImportForm
    success_url = reverse_lazy('customers_overview')

    def form_valid(self, form):
        csv_reader = csv.DictReader(chunk.decode() for chunk in self.request.FILES["input_file"])
        count_successful_imports = 0
        errors = []

        for row in csv_reader:
            try:
                if not Contact.objects.filter(username=row["email"]).exists():
                    company = Company(name=row['company_name'], street=row['street'], number=row['number'],
                                      zipcode=row['zipcode'], city=row['city'])
                    company.save()
                    contact = Contact(company=company, gender=row['gender'], telephone=row['phone'], email=row["email"],
                                      username=row["email"], first_name=row['firstname'], last_name=row['lastname'],
                                      password=row['password'],
                                      language='de')
                    contact.save()
                    address = Address(name=row['street'] + " " + row['number'], street=row['street'],
                                      number=row['number'], zipcode=row['zipcode'], city=row['city'], contact=contact)
                    address.save()

                    group = Group.objects.get(name="client")
                    group.user_set.add(contact)
                    sgroup = Group.objects.get(name='client supervisor')
                    sgroup.user_set.add(contact)
                    count_successful_imports += 1
                else:
                    errors.append(_("User with mail %(mail)s already exists") % {'mail': row['email']})
            except Exception as e:
                errors.append(str(e))
        messages.success(self.request, _("Successfully imported %(total_success)s of %(total)s") %
                         {'total_success': str(count_successful_imports), 'total': csv_reader.line_num - 1})
        if len(errors) > 0:
            messages.error(self.request, ", ".join(errors))
        return super(CustomerImportView, self).form_valid(form)
