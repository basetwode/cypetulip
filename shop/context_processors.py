__author__ = 'Anselm'

from shop.models import (Contact, Order, OrderItem,
                         Product)

def get_open_orders(request):
    open_orders = {}
    if request.user.is_authenticated:
        contact = Contact.objects.filter(user=request.user)
        if contact.count() > 0:
            order = Order.objects.filter(company=contact[0].company, orderdetail__state__isnull=True)
            return collect_open_orders(order)
    elif request.session.session_key:
        order = Order.objects.filter(is_send=False, session=request.session.session_key)
        return collect_open_orders(order)
    else:
        request.session.save()
    return open_orders


def collect_open_orders(order):
    if order.count() > 0:
        items = OrderItem.objects.filter(order=order[0], product__id__in=Product.objects.all())
        all_items = OrderItem.objects.filter(order=order[0])
        sum = 0
        for item in all_items:
            sum += item.product.bprice_wt()
        total = 0
        number_items = 0
        for order in items:
            total += order.product.bprice_wt()
            number_items += 1
        return {'open_orders': items, 'total_cart': total, 'number_items': number_items, 'total_order': sum}
    else:
        return {'open_orders': [], 'total_cart': 0, 'number_items': 0, 'total_order': 0}


def language(request):
    return {'language': 'de'}
