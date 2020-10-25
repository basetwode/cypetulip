from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from management.mixins import NotifyCustomerCreateView
from payment.models import Payment, PaymentDetail
from shop.mixins import EmailConfirmView
from shop.models import Contact, Order, OrderItem, Product, OrderDetail
from shop.utils import create_hash

__author__ = 'Anselm'


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

    def post(self, request, order):
        _order = Order.objects.filter(order_hash=order)
        order_details = OrderDetail.objects.get(order_number=order)
        order_items = OrderItem.objects.filter(order=_order[0], order_item__isnull=True,
                                               product__in=Product.objects.all())
        payment_details = PaymentDetail.objects.get(order=_order[0])
        return render(request, self.template_name,
                      {'order_items': order_items, 'payment_details': payment_details, 'contact': order_details.contact,
                       'shipment': order_details.shipment_address})


class BillSubmitView( EmailConfirmView, View):

    def get(self, request, order):
        _order = Order.objects.filter(order_hash=order)
        order_items = OrderItem.objects.filter(order=_order[0], order_item__isnull=True,
                                               product__in=Product.objects.all())
        payment_details = PaymentDetail.objects.get(order=_order[0])
        payment = Payment(is_paid=False, token=create_hash(), details=payment_details)
        payment.save()
        return redirect(reverse("shop:confirmed_order", args=[order]))

    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        _order = Order.objects.filter(order_hash=order)
        order_items = OrderItem.objects.filter(order=_order[0], order_item__isnull=True,
                                               product__in=Product.objects.all())
        payment_details = PaymentDetail.objects.get(order=_order[0])
        payment = Payment(is_paid=False, token=create_hash(), details=payment_details)
        payment.save()
        self.object = _order[0]
        self.notify_client(contact[0])
        self.notify_staff()
        return redirect(reverse("shop:confirmed_order", args=[order]))
