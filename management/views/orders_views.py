from datetime import datetime

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files import File
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
# Create your views here.
from django.views.generic import DetailView, View, DeleteView
from django_filters.views import FilterView

from billing.utils import calculate_sum
from billing.views.main import GeneratePDFFile
from management.filters.filters import OrderDetailFilter
from management.forms.forms import OrderDetailForm, OrderForm, OrderItemForm
from payment.models import PaymentDetail, Payment, PaymentMethod, PAYMENTMETHOD_BILL_NAME
from permissions.mixins import LoginRequiredMixin
from shipping.models import Shipment
from shop.models import Contact, Order, OrderItem, Product, Employee, OrderDetail, OrderState, \
    IndividualOffer
from shop.utils import get_orderitems_once_only
from shop.utils import json_response
from shop.views.mixins import WizardView, RepeatableWizardView
from utils.mixins import EmailMixin, PaginatedFilterViews
from utils.views import CreateUpdateView


class ManagementOrderOverview(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    model = OrderDetail
    template_name = 'management/orders/orders-overview.html'
    paginate_by = 20
    filterset_class = OrderDetailFilter

    def get_queryset(self):
        return super(ManagementOrderOverview, self).get_queryset().filter(state__isnull=False) \
            .order_by('-date_added')


class ManagementOrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'management/orders/orders-order-detail.html'
    model = Order
    slug_url_kwarg = 'order'
    slug_field = 'order_hash'
    filterset_class = OrderDetailFilter

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
    email_template = 'management/mail/mail-orderacceptedinvoice.html'

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
            return reverse_lazy('management_order_detail_view',
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
        return reverse_lazy('order_create_view', kwargs={'id': self.get_parent_id()})

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
    template_name = 'management/orders/order-item-create.html'
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
        return reverse_lazy('management_order_detail_view',
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


class OrderCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    model = Order
    slug_field = 'order_hash'
    slug_url_kwarg = 'order_hash'
    template_name = 'management/orders/orders-order-create-vue.html'
    fields = '__all__'
    context_object_name = 'order'
    success_message = _('Order created successfully')


class DeleteOrder(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'generic-create-form.html'
    slug_url_kwarg = 'order_hash'
    slug_field = 'order_hash'

    def get_success_url(self):
        messages.success(self.request, _('Order deleted'))
        return reverse_lazy('management_orders_overview')

    def delete(self, request, *args, **kwargs):
        Shipment.objects.filter(order=self.get_object().orderdetail_set.first()).delete()
        return super(DeleteOrder, self).delete(request, *args, **kwargs)
