from django.db.models import Sum
from django.shortcuts import render
# Create your views here.
from django.views import View

from billing.utils import calculate_sum
from payment.models import Payment
from permissions.mixins import LoginRequiredMixin
from shop.models import Order, OrderItem, OrderState, OrderDetail


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
