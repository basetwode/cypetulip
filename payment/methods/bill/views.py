from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from payment.models import Payment, PaymentDetail
from shop.views.mixins import EmailConfirmView
from shop.models import Order, OrderItem, Product, OrderDetail
from shop.utils import create_hash

__author__ = 'Anselm'

# todo: refactor this, use create view
# todo: add gdpr
# todo: add agb and cancellation policy

class BillConfirmView(View):
    template_name = 'bill/confirm.html'

    def get(self, request, order):
        _order = Order.objects.filter(order_hash=order)
        order_details = OrderDetail.objects.get(order_number=order)
        order_items = OrderItem.objects.filter(order=_order[0], order_item__isnull=True,
                                               product__in=Product.objects.all())
        payment_details = PaymentDetail.objects.get(order=_order[0])
        return render(request, self.template_name,
                      {'order_items': order_items, 'payment_details': payment_details, 'contact': order_details.contact,
                       'shipment': order_details.shipment_address})



class BillSubmitView(EmailConfirmView, View):

    def get(self, request, order):
        _order = Order.objects.filter(order_hash=order)
        order_items = OrderItem.objects.filter(order=_order[0], order_item__isnull=True,
                                               product__in=Product.objects.all())
        payment_details = PaymentDetail.objects.get(order=_order[0])
        payment = Payment(is_paid=False, token=create_hash(), details=payment_details)
        payment.save()
        return redirect(reverse("shop:confirmed_order", args=[order]))

    def post(self, request, order):
        _order = Order.objects.filter(order_hash=order)
        order_items = OrderItem.objects.filter(order=_order[0], order_item__isnull=True,
                                               product__in=Product.objects.all())
        payment_details = PaymentDetail.objects.get(order=_order[0])
        payment = Payment(is_paid=False, token=create_hash(), details=payment_details)
        payment.save()
        self.object = _order[0]
        self.notify_client(self.object.orderdetail_set.first().contact)
        self.notify_staff()
        return redirect(reverse("shop:confirmed_order", args=[order]))
