from functools import reduce

# Create your views here.
from django.core.paginator import Paginator
from django.views.generic.list import MultipleObjectMixin
from django_filters.views import FilterView

from accounting.filters.filters import OrderDetailFilter
from payment.models.main import Payment
from permissions.views.mixins import LoginRequiredMixin
from shop.models.orders import OrderState, OrderDetail
from shop.models.products import Product
from utils.mixins import PaginatedFilterViews


class AccountingView(LoginRequiredMixin, PaginatedFilterViews, FilterView, MultipleObjectMixin):
    model = OrderDetail
    template_name = "accounting/accounting-dashboard.html"
    paginate_by = 20
    filterset_class = OrderDetailFilter

    def get_context_data(self, **kwargs):
        filter = OrderDetailFilter(self.request.GET, queryset=OrderDetail.objects.all())

        total_net = reduce(lambda total, order_detail_total: total + order_detail_total,
                           [order_detail.total() for order_detail in filter.qs], 0)

        open_order_state_id = OrderState.objects.get(initial=True).id
        total_gross = reduce(lambda total, order_detail_total: total + order_detail_total,
                             [order_detail.total_discounted_wt() for order_detail in filter.qs], 0)
        last_orders = OrderDetail.objects.all().order_by('-date_added')[:5]

        counted_open_orders = OrderDetail.objects.filter(state__initial=True).count()
        counted_open_shipments = OrderDetail.objects.filter(state__is_paid_state=True).count()
        counted_open_payments = Payment.objects.filter(is_paid=False).count()

        stock_list = Product.objects.all().order_by('stock')
        stock_paginator = Paginator(stock_list, 10)
        stock_page_number = self.request.GET.get('stock-page')
        stock_page_obj = stock_paginator.get_page(stock_page_number)
        # TODO absprung für weitere analysen
        # analyse des kundenumsatzes
        # analyse gearbeitete stunden pro kunde

        return {**super(AccountingView, self).get_context_data(), **{'total_net': total_net, 'total_gross': total_gross,
                                                                     'counted_open_orders': counted_open_orders,
                                                                     'counted_open_payments': counted_open_payments,
                                                                     'counted_open_shipments': counted_open_shipments,
                                                                     'last_orders': last_orders,
                                                                     'open_order_state_id': open_order_state_id,
                                                                     'stock': stock_page_obj}}
