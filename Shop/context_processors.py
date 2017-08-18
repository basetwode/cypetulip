__author__ = 'Anselm'
from  models import Order, OrderDetail, Contact,Company,OrderItem, Product


def get_open_orders(request):
    open_orders = {}
    if request.user.is_authenticated():
        contact = Contact.objects.filter(user=request.user)
        if contact.count() > 0:
            order = Order.objects.filter(is_send=False,company=contact[0].company)
            items =  OrderItem.objects.filter(order=order,product__id__in=Product.objects.all())
            all_items= OrderItem.objects.filter(order=order)
            sum = 0
            for item in all_items:
                sum+=item.product.price
            total = 0
            number_items = 0
            for order in items:
                total+=order.product.price
                number_items+=1
            return {'open_orders':items,'total_cart':total,'number_items':number_items,'total_order':sum}
    return open_orders


def language(request):

    return {'language':request.LANGUAGE_CODE}


