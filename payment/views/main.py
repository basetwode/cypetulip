from django.contrib import messages
from django.shortcuts import redirect
from django.template.defaultfilters import lower
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DetailView

from payment.forms.main import LegalForm, PaymentFormFactory, get_all_payment_forms_as_dict
from payment.models.main import Payment, PaymentDetail
from payment.models.main import PaymentMethod
from shop.models.orders import Order, OrderDetail, OrderState
from shop.models.orders import OrderItem
from shop.models.products import Product
from shop.views.mixins import EmailConfirmView

'''
Creates a new payment and deletes any old ones
This is a shoppingcart view (Step 3)
'''


class PaymentCreateView(CreateView):
    model = PaymentDetail
    template_name = 'payment/payment-create.html'
    slug_field = 'order__uuid'
    slug_url_kwarg = 'order'
    fields = []

    def get_context_data(self, **kwargs):
        payment_methods = PaymentMethod.objects.filter(enabled=True)
        payment_forms = get_all_payment_forms_as_dict()
        for method in payment_methods:
            method.form = PaymentFormFactory(method.provider.api)
        return {**super(PaymentCreateView, self).get_context_data(**kwargs),
                **{'payment_methods': payment_methods, 'forms': payment_forms,
                   'order_details': Order.objects.get(uuid=self.kwargs['order']),
                   'legal_form': LegalForm()}}

    def form_valid(self, form):
        _order = Order.objects.get(uuid=self.kwargs['order'])
        order_details = OrderDetail.objects.get(order=_order)
        order_details.contact = order_details.shipment_address.contact
        order_details.save()

        payment_details = PaymentDetail.objects.filter(order=_order)
        payment_details.delete()

        if not 'method' in self.request.POST:
            return self.form_invalid(form)
        choosen_payment_method = PaymentMethod.objects.get(id=self.request.POST['method'])
        form = PaymentFormFactory(choosen_payment_method.name, self.request.POST)
        legal_form = LegalForm(self.request.POST)
        if form.is_valid() and legal_form.is_valid():
            payment_instance = form.save(commit=False)
            payment_instance.user = order_details.contact
            payment_instance.order = _order
            payment_instance.method = PaymentMethod.objects.get(id=self.request.POST['method'])
            payment_instance.save()
            return redirect(
                reverse('payment:%s' % lower(payment_instance.method.name), kwargs={'order': self.kwargs['order']}))
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Please select a payment method"))
        return super(PaymentCreateView, self).form_invalid(form)


class PaymentConfirmView(DetailView):
    template_name = 'payment/payment-confirm.html'
    slug_url_kwarg = 'order'
    slug_field = 'order__uuid'
    model = PaymentDetail

    def get_context_data(self, **kwargs):
        order_items = OrderItem.objects.filter(order=self.object.order, order_item__isnull=True,
                                               product__in=Product.objects.all())

        return {**super(PaymentConfirmView, self).get_context_data(**kwargs),
                **{'order_items': order_items, 'payment_details': self.object,
                   'contact': self.object.order.orderdetail_set.first().contact,
                   'order_detail': self.object.order.orderdetail_set.first(),
                   'shipment': self.object.order.orderdetail_set.first().shipment_address}}


class PaymentSubmitView(EmailConfirmView, CreateView):
    model = Payment
    fields = []

    def get_success_url(self):
        return reverse_lazy('shop:confirmed_order', kwargs={"uuid":self.kwargs['order']})

    def get_context_data(self, **kwargs):
        return {**super(PaymentSubmitView, self).get_context_data(**kwargs),
                **{}}

    def form_valid(self, form):
        payment = form.save(commit=False)
        payment_details = PaymentDetail.objects.get(order__uuid=self.kwargs['order'])
        order_detail = payment_details.order.orderdetail_set.first()
        payment.is_paid = False
        payment.token = payment_details.order.uuid
        payment.details = payment_details
        if not order_detail.state:
            order_detail.state = OrderState.objects.get(initial=True)
            order_detail.save()
        self.object = payment_details.order
        payment.save()
        self.notify_client(order_detail.contact)
        self.notify_staff()
        return super(PaymentSubmitView, self).form_valid(form)