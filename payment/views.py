from django.shortcuts import redirect, render
from django.template.defaultfilters import lower
from django.urls import reverse, reverse_lazy
from django.views.generic import View, CreateView

from payment.models import PaymentDetail, PaymentMethod
from shop.errors import (FieldError,
                         JsonResponse)
from shop.models import Contact, Order, OrderDetail
from shop.order.utils import get_order_for_hash_and_contact
from shop.utils import json_response, check_params
from .methods.forms import PaymentFormFactory, get_all_payment_forms_as_dict, LegalForm


class PaymentView(View):
    template_name = 'payment.html'
    context_object_name = 'payment_methods'
    model = PaymentMethod

    def get(self, request, order):
        payment_methods = PaymentMethod.objects.filter(enabled=True)
        payment_forms = get_all_payment_forms_as_dict()
        for method in payment_methods:
            method.form = PaymentFormFactory(method.provider.api)
        return render(request, self.template_name, { 'payment_methods': payment_methods, 'forms': payment_forms, 'legal_form': LegalForm()})

    def post(self, request, order):
        payment_methods = PaymentMethod.objects.filter(enabled=True)
        payment_forms = get_all_payment_forms_as_dict()
        for method in payment_methods:
            method.form = PaymentFormFactory(method.provider.api)
        order_object = get_order_for_hash_and_contact(Contact.objects.filter(user_ptr=request.user), order)
        return render(request, self.template_name,
                      {'order_details': order_object, 'payment_methods': payment_methods, 'forms': payment_forms, 'legal_form': LegalForm()})


class PaymentConfirmationView(View):
    template_name = 'order/payment.html'

    def get(self, request, order):
        return redirect('/shop/overview/' + order)

    def post(self, request, order):
        contact = Contact.objects.filter(user_ptr=request.user)
        company = contact[0].company
        _order = Order.objects.get(order_hash=order, is_send=False, company=company)
        payment_details = PaymentDetail.objects.get(order=_order, user=contact)
        self.find_view_by_payment(payment_details)
        pass

    def paypal(self, request, order):
        # create an paymentdetail object here and save it, then redirect to paypal view page
        pass

    def find_view_by_payment(self, payment_detail):
        payment_method = payment_detail.method

        print(payment_method)


class PaymentCreationView(CreateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = PaymentDetail
    model = PaymentDetail
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('shop:address_overview')

    @check_params(required_arguments={'method': '[0-9]'}, message="Please select a payment method")
    def post(self, request, order):
        _order = Order.objects.get(order_hash=order)
        order_details = OrderDetail.objects.get(order=_order)
        order_details.contact = order_details.shipment_address.contact
        order_details.save()

        payment_details = PaymentDetail.objects.filter(order=_order)
        payment_details.delete()

        choosen_payment_method = PaymentMethod.objects.get(id=request.POST['method'])
        form = PaymentFormFactory(choosen_payment_method.name, request.POST)
        legal_form = LegalForm(request.POST)
        if form.is_valid() and legal_form.is_valid():
            payment_instance = form.save(commit=False)
            payment_instance.user = order_details.contact
            payment_instance.order = _order
            payment_instance.method = PaymentMethod.objects.get(id=request.POST['method'])
            payment_instance.save()
            result = json_response(code=200, x=JsonResponse(
                next_url=reverse('payment:%s' % lower(payment_instance.method.name),
                                 args=[order])).dump())
        else:
            result = self.__form_is_not_valid(form, legal_form)

        return result

    def paypal(self, order, form):
        pass

    def __form_is_not_valid(self, form1, form2):
        form_items = {**form1.errors, **form2.errors}
        errors = [FieldError(field_name=k, message=v) for k, v in form_items.items()]
        error_list = JsonResponse(errors=errors, success=False)
        return json_response(code=400, x=error_list.dump())
