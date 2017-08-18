from django.shortcuts import redirect, render
from django.views.generic import View
from Shop.models import Contact, Order, OrderItem, Product
from Shop.order.utils import get_orderitems_once_only

__author__ = 'Anselm'


class OverviewView(View):
    template_name = 'order/overview.html'

    def get(self, request, order):
        return redirect('/shop/checkout/' + order)

    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.filter(order_hash=order, is_send=False, company=company)
        if _order.count() > 0 and _order[0].token == request.POST.get('token'):
            ord = _order[0]
            # ord.token = None
            ord.save()
            order_items = OrderItem.objects.filter(order=_order, order_item__isnull=True,product__in=Product.objects.all())
            return render(request, self.template_name, {'order_details': _order[0],
                                                        'order_items': order_items,
                                                        'order_items_once_only': get_orderitems_once_only(ord)})
        else:
            return redirect('/shop/checkout/' + order)

