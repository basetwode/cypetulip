from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from payment.models import Payment, PaymentDetails
from permissions.permissions import check_serve_perms
from shop.models import Contact, Order, OrderItem, Product
from shop.utils import create_hash

__author__ = 'Anselm'


class BillConfirmView(View):
    template_name = 'bill/confirm.html'

    @check_serve_perms
    def get(self, request, order):
        print('bill')
        pass

    @check_serve_perms
    def post(self, request, order):
        print('bill post')
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.filter(order_hash=order, is_send=False, company=company)
        order_items = OrderItem.objects.filter(order=_order, order_item__isnull=True, product__in=Product.objects.all())
        payment_details = PaymentDetails.objects.get(order=_order, user=contact[0])
        return render(request, self.template_name, {'order_items': order_items, 'payment_details': payment_details})


class BillSubmitView(View):

    @check_serve_perms
    def get(self, request, order):
        pass

    @check_serve_perms
    def post(self, request, order):
        print('bill submit')
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.filter(order_hash=order, is_send=False, company=company)
        order_items = OrderItem.objects.filter(order=_order, order_item__isnull=True, product__in=Product.objects.all())
        payment_details = PaymentDetails.objects.get(order=_order, user=contact[0])
        payment = Payment(is_paid=False, token=create_hash(), details=payment_details)
        payment.save()

        return redirect(reverse("confirmed_order", args=[order]))
