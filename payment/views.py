
from django.shortcuts import redirect, render
from django.template.defaultfilters import lower
from django.urls import reverse
from django.views.generic import View

from payment.models import PaymentDetails, PaymentMethod
from permissions.permissions import check_serve_perms
from shop.Errors import (FieldError,
                         JsonResponse)
from shop.models import Contact, Order
from shop.order.utils import get_order_for_hash_and_contact
from shop.utils import json_response, check_params
from .methods.forms import PaymentFormFactory, get_all_payment_forms_as_dict


class PaymentView(View):
    template_name = 'payment.html'

    @check_serve_perms
    def get(self, request, order):
        return redirect('/shop/overview/' + order)

    @check_serve_perms
    def post(self, request, order):
        payment_methods = PaymentMethod.objects.all()
        payment_forms = get_all_payment_forms_as_dict()
        for method in payment_methods:
            method.form = PaymentFormFactory(method.name)
        order_object = get_order_for_hash_and_contact(Contact.objects.filter(user=request.user), order)
        return render(request, self.template_name,
                      {'order_details': order_object, 'payment_methods': payment_methods, 'forms': payment_forms})


class PaymentConfirmationView(View):
    template_name = 'order/payment.html'

    @check_serve_perms
    def get(self, request, order):
        return redirect('/shop/overview/' + order)

    @check_serve_perms
    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.get(order_hash=order, is_send=False, company=company)
        payment_details = PaymentDetails.objects.get(order=_order, user=contact,
                                                     )
        self.find_view_by_payment(payment_details)
        pass

    def paypal(self, request, order):
        # create an paymentdetail object here and save it, then redirect to paypal view page
        pass

    def find_view_by_payment(self, payment_detail):
        payment_method = payment_detail.method

        print(payment_method)


class PaymentCreationView(View):
    template_name = 'order/payment.html'

    @check_serve_perms
    def get(self, request, order):
        return redirect('/shop/overview/' + order)

    @check_serve_perms
    @check_params(required_arguments={'method': '[0-9]'}, message="Please select a payment method")
    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.get(order_hash=order, is_send=False, company=company)

        payment_details = PaymentDetails.objects.filter(order=_order, user=contact[0])
        payment_details.delete()

        choosen_payment_method = PaymentMethod.objects.get(id=request.POST['method'])
        form = PaymentFormFactory(choosen_payment_method.name, request.POST)
        if form.is_valid():
            payment_instance = form.save(commit=False)
            payment_instance.user = Contact.objects.get(user=request.user)
            payment_instance.order = _order
            payment_instance.method = PaymentMethod.objects.get(id=request.POST['method'])
            payment_instance.save()
            result = json_response(code=200, x=JsonResponse(
                # next_url=reverse('payment:methods:bill:index')).dump())
                next_url=reverse('payment:%s' % lower(payment_instance.method.name),
                                 args=[order])).dump())
        else:
            result = self.__form_is_not_valid(form)

        return result

    def paypal(self, order, form):
        pass

    def __form_is_not_valid(self, form):
        errors = [FieldError(field_name=k, message=v) for k, v in form.errors.items()]
        error_list = JsonResponse(errors=errors, success=False)
        return json_response(code=400, x=error_list.dump())
