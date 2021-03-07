from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import View, TemplateView, DetailView, FormView, UpdateView

from shop.forms.shoppingcart_forms import OrderItemForm
from shop.models.orders import OrderState, OrderDetail, OrderItem
from shop.models.products import ProductSubItem, Product
from shop.models.accounts import Contact

__author__ = 'Anselm'


class ShoppingCartDetailView(DetailView):
    template_name = 'shop/shoppingcart/shoppingcart-cart.html'
    model = OrderDetail
    context_object_name = 'order_details'

    def get_object(self, queryset=None):
        return OrderDetail.objects.get(state__isnull=True,
                                 company=Contact.objects.get(
                                     user_ptr=self.request.user).company) if self.request.user.is_authenticated \
            else OrderDetail.objects.get(is_send=False, session=self.request.session.session_key)


class ShoppingCartAddItemView(FormView):
    template_name = 'shop/products/products-product-overview.html'
    form_class = OrderItemForm

    def get_success_url(self):
        return reverse_lazy('shop:products', args=self.args)

    def form_valid(self, form):
        response = super(ShoppingCartAddItemView, self).form_valid(form)

        product = self.validate_and_get_product(form)
        if not product:
            return self.form_invalid(form)

        order = self.get_or_create_order()

        stock_sufficient = self.validate_product_stock(form, order, product)
        if not stock_sufficient:
            return self.form_invalid(form)

        self.create_orderitem(order, product)
        return response

    def validate_and_get_product(self, form):
        product = Product.objects.filter(name=self.kwargs['name'], category__path=self.kwargs['path'],
                                         price_on_request=False)
        if product.count() > 0:
            return product.first()
        else:
            messages.error(self.request, _('We\'re sorry, we can not add %(article)s to your shopping '
                                           'cart because it can only be ordered using our individual offer form') % {
                               'article': self.kwargs['name']})
            form.add_error("product", _("Product unavailable"))
            return None

    def validate_product_stock(self, form, order, product):
        if product.is_stock_sufficient(order):
            return True
        else:
            messages.error(self.request, _('We\'re sorry, we can not add %(article)s to your shopping '
                                           'cart because our stocks are insufficient') % {
                               'article': self.kwargs['name']})
            form.add_error("product", _("Insufficient product stock"))
            return False

    def get_or_create_order(self):
        contact = Contact.objects.filter(user_ptr=self.request.user) if self.request.user.is_authenticated else None
        order = OrderDetail.objects.filter(state__isnull=True,
                                     company=contact.first().company) if self.request.user.is_authenticated else \
            OrderDetail.objects.filter(is_send=False, session=self.request.session.session_key)
        order = OrderDetail.create_new_order(self.request) if order.count() == 0 else order.first()
        return order

    def create_orderitem(self, order_detail, product):
        item = OrderItem(order_detail=order_detail, product=product, count=1)
        item.save()


class DeliveryView(DetailView):
    model = OrderDetail
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    template_name = 'shop/shoppingcart/shoppingcart-delivery.html'
    context_object_name = 'order_detail'


class OrderConfirmedView(DetailView):
    model = OrderDetail
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    template_name = 'shop/shoppingcart/shoppingcart-orderconfirmed.html'
    context_object_name = 'order_detail'
    fields = []

