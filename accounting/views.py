import zipfile
from functools import reduce

from django.core.files import File
from django.core.paginator import Paginator
from django.http import HttpResponse
# Create your views here.
from django.views.generic.list import MultipleObjectMixin
from django_filters.views import FilterView
from six import BytesIO

from accounting.filters import OrderDetailFilter
from billing.views import GeneratePDFFile
from payment.models import Payment
from permissions.mixins import LoginRequiredMixin
from shop.models import OrderState, OrderDetail, Product
from utils.mixins import PaginatedFilterViews


class AccountingView(LoginRequiredMixin, PaginatedFilterViews, FilterView, MultipleObjectMixin):
    model = OrderDetail
    template_name = "accounting-dashboard.html"
    paginate_by = 20
    filterset_class = OrderDetailFilter

    def get_context_data(self, **kwargs):
        filter = OrderDetailFilter(self.request.GET, queryset=OrderDetail.objects.all())

        total_net = reduce(lambda total, order_detail_total: total + order_detail_total,
                           [order_detail.total() for order_detail in filter.qs], 0)

        open_order_state_id = OrderState.objects.get(initial=True).id
        total_gross = reduce(lambda total, order_detail_total: total + order_detail_total,
                             [order_detail.total_discounted_wt() for order_detail in filter.qs], 0)
        last_orders = OrderDetail.objects.all()[:5]

        counted_open_orders = OrderDetail.objects.filter(state__initial=True).count()
        counted_open_shipments = OrderDetail.objects.filter(state__is_paid_state=True).count()
        counted_open_payments = Payment.objects.filter(is_paid=False).count()

        # related_orderitems = OrderItem.objects.filter(order_detail__in=OrderDetail.objects.filter(orderitem__product=self),
        #                                               order_item__isnull=True).exclude(product=self).order_by('product')
        #
        # amount_per_month = OrderDetail.objects.all() \
        #     .annotate(ocount=Count('orderitem', filter=Q(orderitem__in=related_orderitems))) \
        #     .filter(ocount__gt=0) \
        #     .order_by('-ocount')

        stock_list = Product.objects.filter(stock__lt=10).order_by('stock')
        stock_paginator = Paginator(stock_list, 10)
        stock_page_number = self.request.GET.get('stock-page')
        stock_page_obj = stock_paginator.get_page(stock_page_number)
        # TODO zurück zum accounting link im menü
        # TODO absprung für weitere analysen
        # analyse des kundenumsatzes
        # analyse gearbeitete stunden pro kunde

        return {**super(AccountingView, self).get_context_data(), **{'total_net': total_net, 'total_gross': total_gross,
                                                                     'counted_open_orders': counted_open_orders,
                                                                     'filter': filter,
                                                                     'counted_open_payments': counted_open_payments,
                                                                     'counted_open_shipments': counted_open_shipments,
                                                                     'last_orders': last_orders,
                                                                     'open_order_state_id': open_order_state_id,
                                                                     'stock': stock_page_obj,
                                                                     'amount_per_month': ''}}


class AccountingViewExportCSV(AccountingView):
    template_name = "export/accounting.csv"
    content_type = 'text/csv'

    def get(self, request, *args, **kwargs):
        response = super(AccountingViewExportCSV, self).get(request, *args, **kwargs)
        filename = "accounting%s.csv" % ''
        content = "attachment; filename=%s" % filename
        response['Content-Disposition'] = content
        return response


class AccountingFullExport(AccountingViewExportCSV):
    content_type = 'application/x-zip-compressed'

    def get(self, request, *args, **kwargs):
        response_csv = super(AccountingFullExport, self).get(request, *args, **kwargs)
        response = HttpResponse(self.create_zip(response_csv))
        filename = "accounting%s.zip" % ''
        content = "attachment; filename=%s" % filename
        response['Content-Disposition'] = content
        return response

    def create_zip(self, csv):
        s = BytesIO()
        # The zip compressor
        zf = zipfile.ZipFile(s, "w")
        for order_detail in self.get_context_data().get("filter").qs:
            if order_detail.bill_file:
                zf.write(order_detail.bill_file.path, f"{order_detail.unique_bill_nr()}.pdf")
            else:
                try:
                    pdf = GeneratePDFFile().generate(order_detail.order)
                    order_detail.bill_file = File(pdf, f"I_{order_detail.unique_bill_nr()}.pdf")
                    order_detail.save()
                    zf.write(order_detail.bill_file.path, f"{order_detail.unique_bill_nr()}.pdf")
                except:
                    pass
        zf.writestr("accounting.csv", csv.rendered_content)
        zf.close()
        return s.getvalue()
