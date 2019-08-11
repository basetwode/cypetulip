from shop.models import OrderItem, Product, Order

__author__ = 'Anselm'



def get_orderitems_once_only( order):
        order_items = OrderItem.objects.filter(order=order, order_item__isnull=True).exclude(
            product__in=Product.objects.all())
        return  order_items

def get_order_for_hash_and_contact(contact,order_hash):
    company = contact[0].company
    order = Order.objects.filter(order_hash=order_hash, is_send=False, company=company)
    if order.count() > 0:
        order = order[0]
        return order
    return None