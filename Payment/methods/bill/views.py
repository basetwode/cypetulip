from django.urls import reverse
from django.shortcuts import redirect, render
from django.views.generic import View

from Payment.models import PaymentDetails, Payment
from Permissions.permissions import check_serve_perms
from Shop.models import Order, OrderItem, Contact, Product
from Shop.utils import create_hash

__author__ = 'Anselm'

class BillConfirmView(View):
    template_name = 'bill/confirm.html'

    @check_serve_perms
    def get(self, request, order):
        pass

    @check_serve_perms
    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.filter(order_hash=order, is_send=False, company=company)
        order_items = OrderItem.objects.filter(order=_order, order_item__isnull=True, product__in=Product.objects.all())
        payment_details = PaymentDetails.objects.get(order=_order, user=contact)
        return render(request, self.template_name, {'order_items':order_items, 'payment_details':payment_details})

class BillSubmitView(View):

    @check_serve_perms
    def get(self, request, order):
        pass

    @check_serve_perms
    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.filter(order_hash=order, is_send=False, company=company)
        order_items = OrderItem.objects.filter(order=_order, order_item__isnull=True, product__in=Product.objects.all())
        payment_details = PaymentDetails.objects.get(order=_order, user=contact)
        payment = Payment(is_paid=False,token=create_hash(),details=payment_details)
        payment.save()

        return redirect(reverse("confirmed_order", args=[order]))
