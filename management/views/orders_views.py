import logging
import zipfile
from datetime import datetime

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
# Create your views here.
from django.views.generic import DetailView, View, DeleteView, UpdateView
from django_filters.views import FilterView
from six import BytesIO

from billing.utils import calculate_sum
from billing.views.main import GeneratePDFFile
from management.filters.filters import OrderDetailFilter
from payment.models.main import PaymentDetail, Payment
from permissions.views.mixins import LoginRequiredMixin
from shipping.models.main import Shipment
from shop.models.accounts import Employee
from shop.models.orders import OrderState, OrderDetail, OrderItem
from shop.models.products import Product
from shop.utils import get_orderitems_once_only
from shop.utils import json_response
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
    model = OrderDetail
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'
    filterset_class = OrderDetailFilter

    def get_context_data(self, **kwargs):
        employees = Employee.objects.all()
        _payment_details = None
        _payment = None
        try:
            _payment_details = PaymentDetail.objects.get(order_detail=self.object)
            _payment = Payment.objects.get(details=_payment_details)
        except:
            pass
        _states = OrderState.objects.all()
        order_items = OrderItem.objects.filter(order_detail=self.object, order_item__isnull=True,
                                               product__in=Product.objects.all())

        total = calculate_sum(order_items)
        return {**super(ManagementOrderDetailView, self).get_context_data(**kwargs), **
        {'order_detail': self.object,  'contact': self.object.contact, 'total': total,
         'order_items': order_items, 'employees': employees,
         'order_items_once_only': get_orderitems_once_only(self.object), 'payment': _payment,
         'payment_details': _payment_details, 'states': _states}}


class OrderAssignEmployeeView(LoginRequiredMixin, View):
    def post(self, request, uuid):
        _order = OrderDetail.objects.get(uuid=uuid)
        _employee = Employee.objects.get(id=request.POST['id'])
        _order.assigned_employee = _employee
        try:
            _order.save()
            return json_response(200, x={})
        except:
            return json_response(500, x={})


class OrderPayView(View):
    def post(self, request, uuid):
        _order_detail = OrderDetail.objects.get(uuid=uuid)
        _payment_detail = PaymentDetail.objects.get(order_detail=_order_detail)
        _payment = Payment.objects.get(details=_payment_detail)
        _payment.is_paid = True
        _order_detail.state = OrderState.objects.get(is_paid_state=True)
        _order_detail.save()
        try:
            _payment.save()
            messages.success(request, _("Order saved"))
            return redirect(request.META.get('HTTP_REFERER'))
        except:
            return json_response(500, x={})


class OrderShipView(View):
    def post(self, request, uuid):
        _order = OrderDetail.objects.get(uuid=uuid)
        _order.is_send = True
        try:
            _order.save()
            return redirect(request.META.get('HTTP_REFERER'))
        except:
            return json_response(500, x={})


class OrderChangeStateView(View):
    def post(self, request, uuid):
        _order = OrderDetail.objects.get(uuid=uuid)
        _next_state = OrderState.objects.get(id=request.POST['id'])
        _order.state = _next_state
        try:
            _order.save()
            return redirect(request.META.get('HTTP_REFERER'))
        except:
            return json_response(500, x={})


class OrderAcceptInvoiceView(View, EmailMixin):
    email_template = 'management/mail/mail-orderacceptedinvoice.html'

    def post(self, request, uuid):
        _order = OrderDetail.objects.get(uuid=uuid)

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
            logging.exception(_("Something went wrong"))
            messages.error(request, _("Something went wrong"))
            return redirect(request.META.get('HTTP_REFERER'))

    def send_invoice(self, _order, ):
        if not _order.bill_number:
            _order.bill_number = (OrderDetail.objects.filter(bill_number__isnull=False).order_by(
                'bill_number').last().bill_number + 1) \
                if OrderDetail.objects.filter(bill_number__isnull=False).exists() else 1
            _order.save()
        pdf = GeneratePDFFile().generate(_order.uuid)
        _order.bill_file = File(pdf, f"I_{_order.unique_bill_nr()}.pdf")
        _order.save()
        total = calculate_sum(_order.orderitem_set, True)
        self.send_mail(_order.contact, _('Your Invoice ') + _order.unique_bill_nr(), '',
                       {'object': _order,
                        'contact': _order.contact,
                        'total': total,
                        'order_detail': _order,
                        'files': {_(
                            'Invoice') + "_" + _order.unique_bill_nr() +
                                  ".pdf": _order.bill_file},
                        'host': self.request.META[
                            'HTTP_HOST']},
                       _order.contact.billing_mail)


class OrderCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    model = OrderDetail
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    template_name = 'management/orders/orders-order-create-vue.html'
    fields = '__all__'
    context_object_name = 'order'
    success_message = _('Order created successfully')


class DeleteOrder(LoginRequiredMixin, DeleteView):
    model = OrderDetail
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'

    def get_success_url(self):
        messages.success(self.request, _('Order deleted'))
        return reverse_lazy('management_orders_overview')

    def delete(self, request, *args, **kwargs):
        Shipment.objects.filter(order_detail=self.get_object()).delete()
        return super(DeleteOrder, self).delete(request, *args, **kwargs)


class ManagementOrderExportCSV(ManagementOrderOverview):
    template_name = "management/orders/export/orders.csv"
    content_type = 'text/csv'

    def get(self, request, *args, **kwargs):
        response = super(ManagementOrderExportCSV, self).get(request, *args, **kwargs)
        filename = "orders%s.csv" % ''
        content = "attachment; filename=%s" % filename
        response['Content-Disposition'] = content
        return response


class ManagementFullExport(ManagementOrderExportCSV):
    content_type = 'application/x-zip-compressed'

    def get(self, request, *args, **kwargs):
        response_csv = super(ManagementFullExport, self).get(request, *args, **kwargs)
        response = HttpResponse(self.create_zip(response_csv))
        filename = "orders%s.zip" % ''
        content = "attachment; filename=%s" % filename
        response['Content-Disposition'] = content
        return response

    def create_zip(self, csv):
        s = BytesIO()
        # The zip compressor
        zf = zipfile.ZipFile(s, "w")
        for order_detail in self.filterset.qs:
            if order_detail.bill_file:
                zf.write(order_detail.bill_file.path, f"{order_detail.unique_bill_nr()}.pdf")
            else:
                try:
                    pdf = GeneratePDFFile().generate(order_detail)
                    order_detail.bill_file = File(pdf, f"I_{order_detail.unique_bill_nr()}.pdf")
                    order_detail.save()
                    zf.write(order_detail.bill_file.path, f"{order_detail.unique_bill_nr()}.pdf")
                except:
                    pass
        zf.writestr("orders.csv", csv.rendered_content)
        zf.close()
        return s.getvalue()


class OrderCancelView(UpdateView):
    model = OrderDetail
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'
    fields = []

    def get_success_url(self):
        messages.success(self.request, _("Order canceled!"))
        return reverse_lazy('management_order_detail_view', kwargs={'uuid': self.object.uuid})

    def form_valid(self, form):
        resp = super(OrderCancelView, self).form_valid(form)
        self.object.state = OrderState.objects.get(initial=True).cancel_order_state
        self.object.save()
        return resp