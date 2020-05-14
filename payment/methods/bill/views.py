from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from payment.models import Payment, PaymentDetail
from shop.models import Contact, Order, OrderItem, Product, OrderDetail
from shop.utils import create_hash

__author__ = 'Anselm'


class BillConfirmView(View):
    template_name = 'bill/confirm.html'

    def get(self, request, order):
        pass

    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.filter(order_hash=order, is_send=False, company=company)
        order_details = OrderDetail.objects.get(order_number=order)
        order_items = OrderItem.objects.filter(order=_order[0], order_item__isnull=True,
                                               product__in=Product.objects.all())
        payment_details = PaymentDetail.objects.get(order=_order[0], user=contact[0])
        return render(request, self.template_name,
                      {'order_items': order_items, 'payment_details': payment_details, 'contact': contact[0],
                       'shipment': order_details.shipment_address})


class BillSubmitView(View):

    def get(self, request, order):
        pass

    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.filter(order_hash=order, is_send=False, company=company)
        order_items = OrderItem.objects.filter(order=_order[0], order_item__isnull=True,
                                               product__in=Product.objects.all())
        payment_details = PaymentDetail.objects.get(order=_order[0], user=contact[0])
        payment = Payment(is_paid=False, token=create_hash(), details=payment_details)
        payment.save()

        return redirect(reverse("shop:confirmed_order", args=[order]))
