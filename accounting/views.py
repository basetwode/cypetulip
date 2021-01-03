import datetime
from functools import reduce

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.
from django.views import View
from django_filters.views import FilterView

from accounting.filters import OrderDetailFilter
from billing.utils import calculate_sum
from payment.models import Payment
from permissions.mixins import LoginRequiredMixin
from shop.models import Order, OrderItem, OrderState, OrderDetail
from utils.mixins import PaginatedFilterViews


class AccountingView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    model = OrderDetail
    template_name = "accounting-dashboard.html"
    paginate_by = 20
    filterset_class = OrderDetailFilter


    def get_context_data(self, **kwargs):

        filter = OrderDetailFilter(self.request.GET, queryset=OrderDetail.objects.all())

        total_netto =reduce(lambda total, order_detail_total: total + order_detail_total,
                            [order_detail.total() for order_detail in filter.qs], 0)

        last_orders = OrderDetail.objects.all()[:5]
        open_order_state_id = OrderState.objects.get(initial=True).id
        all_order_items = OrderItem.objects.filter()
        total_brutto =reduce(lambda total, order_detail_total: total + order_detail_total,
                             [order_detail.total_discounted_wt() for order_detail in filter.qs],0)
        last_orders = OrderDetail.objects.all()[:5]

        counted_open_orders = OrderDetail.objects.filter(state__initial=True).count()
        counted_open_shipments = OrderDetail.objects.filter(state__is_paid_state=True).count()
        counted_open_payments = Payment.objects.filter(is_paid=False).count()


        return {**super(AccountingView, self).get_context_data(), **{'total_netto': total_netto, 'total_brutto': total_brutto,
                       'counted_open_orders': counted_open_orders, 'filter': filter,
                       'counted_open_payments': counted_open_payments, 'counted_open_shipments': counted_open_shipments,
                       'last_orders': last_orders, 'open_order_state_id': open_order_state_id}}


class AccountingViewExportCSV(AccountingView):
    template_name = "export/accounting.csv"
    content_type = 'text/csv'

    def get(self, request, *args, **kwargs):

        response = super(AccountingViewExportCSV, self).get(request,*args,**kwargs)
        filename = "accounting%s.csv" % '_asd'
        content = "attachment; filename=%s" % filename
        response['Content-Disposition'] = content
        return response
