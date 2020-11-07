from datetime import datetime

from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
# Create your views here.
from django.views.generic import DetailView, ListView, View, DeleteView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.utils.translation import ugettext_lazy as _
from django_filters.views import FilterView

from billing.utils import calculate_sum
from billing.views import GeneratePDFFile
from management.filters import OrderDetailFilter
from permissions.mixins import LoginRequiredMixin, PermissionPostGetRequiredMixin

from cms.models import Page, Section
from management.models import LdapSetting, MailSetting, LegalSetting, ShopSetting
from payment.models import PaymentDetail, Payment, PaymentMethod, PAYMENTMETHOD_BILL_NAME, PaymentProvider
from shipping.models import Shipment
from shop.filters import ProductFilter, ContactFilter, ProductCategoryFilter, SectionFilter, \
    PageFilter, ShipmentPackageFilter, FileSubItemFilter
from management.forms import OrderDetailForm, OrderForm, OrderItemForm, PaymentProviderForm
from shop.mixins import WizardView, RepeatableWizardView
from shop.models import Contact, Order, OrderItem, Product, ProductCategory, Company, Employee, OrderDetail, OrderState, \
    FileSubItem, IndividualOffer
from shop.order.utils import get_orderitems_once_only
from shop.utils import json_response
from utils.mixins import EmailMixin, PaginatedFilterViews
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


class ManagementOrderOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    model = OrderDetail
    template_name = 'orders-overview.html'
    paginate_by = 20
    filterset_class = OrderDetailFilter

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ManagementOrderOverviewView, self).get_context_data(**kwargs)
        return {**context, **{'employees': Employee.objects.all()}}

    def get_queryset(self):
        return super(ManagementOrderOverviewView, self).get_queryset().filter(state__isnull=False)\
            .order_by('-date_added')


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
            order_items = OrderItem.objects.filter(order=_order, order_item__isnull=True,
                                                   product__in=Product.objects.all())

            total = calculate_sum(order_items)
            return render(request, self.template_name,
                          {'order_details': _order, 'order': _order, 'contact': contact, 'total': total,
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


class ShopSettingsDetailView(LoginRequiredMixin, CreateUpdateView):
    template_name = 'settings-details.html'
    shop_settings_id = None
    slug_field = 'id'
    slug_url_kwarg = 'shop_settings_id'
    model = ShopSetting
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('shop_settings_details', kwargs={'shop_settings_id': self.object.id})


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
        pdf = GeneratePDFFile().generate(_order.order)
        total = calculate_sum(_order.order.orderitem_set, True)
        self.send_mail(_order.contact, _('Your Invoice ')+_order.unique_nr(),'',{'object':_order.order,
                                                                                 'contact': _order.contact,
                                                                                 'total' : total,
                                                                                 'order': _order.order,
                                                                                 'files': {_('Invoice')+"_"+_order.unique_nr()+
                                                                                           ".pdf":pdf.getvalue()},
                                                                                 'host': self.request.META['HTTP_HOST']})




class ShipmentOverviewView(LoginRequiredMixin, ListView):
    template_name = 'shipment-overview.html'
    context_object_name = 'shipment'
    model = Shipment

    def get(self, request, *args, **kwargs):
        filter = ShipmentPackageFilter(request.GET, queryset=Shipment.objects.all())
        return render(request, self.template_name,
                      {'filter': filter})


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


class DeleteOrder(DeleteView):
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


class CreateOrderView(WizardView):
    page_title = _('Select customer')
    template_name = 'generic-create-form.html'
    order_id = None
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = Order
    form_class = OrderForm

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
        return reverse_lazy('create_order_detail', kwargs={'parent_id':self.object.id, 'id': order_detail.id})


class CreateOrderDetailView(WizardView):
    page_title = _('Define order details')
    model = OrderDetail
    pk_url_kwarg = 'id'
    form_class = OrderDetailForm

    def get_back_url(self):
        return reverse_lazy('create_order', kwargs={'id': self.get_parent_id()})

    def get_success_url(self):
        return reverse_lazy('create_order_item', kwargs={'id': '', 'parent_id':self.get_object().id})

    def form_valid(self, form):
        order_detail = form.save(commit=False)
        if order_detail.state is None:
            order_detail.state = OrderState.objects.get(initial=True)
        form.save()
        if order_detail.order.paymentdetail_set.count() == 0:
            payment_detail = PaymentDetail(order=order_detail.order, method=PaymentMethod.objects.get(name=PAYMENTMETHOD_BILL_NAME),
                                       user=order_detail.contact)
            payment_detail.save()
            payment = Payment(details=payment_detail, is_paid=False)
            payment.save()

        return super(CreateOrderDetailView, self).form_valid(form)

    def get_form_kwargs(self):
        form_kwargs = super(CreateOrderDetailView, self).get_form_kwargs()
        return {**form_kwargs, **{'contacts':Contact.objects.filter(company=self.object.order.company)}}


class CreateOrderItem(RepeatableWizardView):
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
                                                           'parent_id': OrderDetail.objects.get(id=self.get_parent_id()).order.id})

    def get_next_url(self):
        return reverse_lazy('management_detail_order',
                            kwargs={'order': OrderDetail.objects.get(id=self.get_parent_id()).order.order_hash})

    def get_success_url(self):
        return reverse_lazy('create_order_item', kwargs={'id':'', 'parent_id':self.get_parent_id()})


class DeleteOrderItem(DeleteView):
    model = OrderItem
    template_name = 'generic-create-form.html'
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse_lazy('create_order_item', kwargs={'id': '',
                                                           'parent_id': OrderDetail.objects.get(id=self.kwargs['parent_id']).id})


class PaymentProviderSettings(FormView):
    template_name = 'payment-settings.html'
    form_class = PaymentProviderForm
    success_url = reverse_lazy('payment_settings_details')

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

        invoice_method.save()
        prepayment_method.save()
        paypal_method.save()
        paypal_provider.save()
        messages.success(self.request, _("Payment settings saved!"))
        return super(PaymentProviderSettings, self).form_valid(form)

    def get_initial(self):
        initial = super(PaymentProviderSettings, self).get_initial()
        paypal_provider,created = PaymentProvider.objects.get_or_create(api="PayPal")
        paypal_method,created = PaymentMethod.objects.get_or_create(provider=paypal_provider, name="PayPal")
        invoice_provider,created = PaymentProvider.objects.get_or_create(api="Bill")
        invoice_method,created = PaymentMethod.objects.get_or_create(provider=invoice_provider, name="Bill")
        prepayment_provider,created = PaymentProvider.objects.get_or_create(api="Prepayment")
        prepayment_method,created = PaymentMethod.objects.get_or_create(provider=prepayment_provider, name="Prepayment")
        initial.update({'prepayment_enabled': prepayment_method.enabled,
                        'prepayment_description': prepayment_method.details,
                        'invoice_enabled': invoice_method.enabled,
                        'invoice_description': invoice_method.details,
                        'paypal_enabled': paypal_method.enabled,
                        'paypal_description': paypal_method.details,
                        'paypal_user': paypal_provider.user_name,
                        'paypal_secret': paypal_provider.secret,
                        })
        return initial



