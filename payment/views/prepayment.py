from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView

from payment.models.main import Payment, PaymentDetail
from shop.models.orders import OrderItem
from shop.models.products import Product
from shop.views.mixins import EmailConfirmView

__author__ = 'Anselm'


class PrepaymentConfirmView(DetailView):
    template_name = 'payment/payment-confirm.html'
    slug_url_kwarg = 'order'
    slug_field = 'order__uuid'
    model = PaymentDetail

    def get_context_data(self, **kwargs):
        order_items = OrderItem.objects.filter(order=self.object.order, order_item__isnull=True,
                                               product__in=Product.objects.all())

        return {**super(PrepaymentConfirmView, self).get_context_data(**kwargs),
                **{'order_items': order_items, 'payment_details': self.object,
                   'contact': self.object.order.orderdetail_set.first().contact,
                   'order_detail': self.object.order.orderdetail_set.first(),
                   'shipment': self.object.order.orderdetail_set.first().shipment_address}}


class PrepaymentSubmitView(EmailConfirmView, CreateView):
    model = Payment
    fields = []

    def get_success_url(self):
        return reverse_lazy('shop:confirmed_order', kwargs={"uuid":self.kwargs['order']})

    def get_context_data(self, **kwargs):
        return {**super(PrepaymentSubmitView, self).get_context_data(**kwargs),
                **{}}

    def form_valid(self, form):
        payment = form.save(commit=False)
        payment_details = PaymentDetail.objects.get(order__uuid=self.kwargs['order'])
        payment.is_paid = False
        payment.token = payment_details.order.uuid
        payment.details = payment_details
        payment.save()
        # TODO: refactor to base payment views, and put this there
        if not self.object.state:
            self.object.state = OrderState.objects.get(initial=True)
            self.object.save()
            if self.object.is_send:
                return redirect(reverse("detail_order", kwargs={'order':self.object.order.uuid}))
            else:
                self.object.is_send = True
                self.object.save()
        self.object = payment_details.order
        self.notify_client(payment_details.order.orderdetail_set.first().contact)
        self.notify_staff()
        return super(PrepaymentSubmitView, self).form_valid(form)

