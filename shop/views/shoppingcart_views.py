from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import View, TemplateView, DetailView, FormView

from shop.forms.shoppingcart_forms import ItemBuilder, SubItemForm, OrderDetail, OrderItemForm
from shop.models import Contact, Order, OrderItem, Product, ProductSubItem, OrderState

__author__ = 'Anselm'


class ShoppingCartDetailView(DetailView):
    template_name = 'shop/shoppingcart/shoppingcart-cart.html'
    model = Order
    context_object_name = 'order_details'

    def get_object(self, queryset=None):
        return Order.objects.get(orderdetail__state__isnull=True,
                                 company=Contact.objects.get(
                                     user_ptr=self.request.user).company) if self.request.user.is_authenticated \
            else Order.objects.get(is_send=False, session=self.request.session.session_key)


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

        order, order_detail = self.get_or_create_order()

        stock_sufficient = self.validate_product_stock(form, order, product)
        if not stock_sufficient:
            return self.form_invalid(form)

        self.create_orderitem(order, order_detail, product)
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
        contact = Contact.objects.filter(user_ptr=self.request.user)
        order = Order.objects.filter(orderdetail__state__isnull=True,
                                     company=contact.first().company) if self.request.user.is_authenticated else \
            Order.objects.filter(is_send=False, session=self.request.session.session_key)
        order, order_detail = Order.create_new_order(self.request) if order.count() == 0 else [order.first(),
                                                                                               OrderDetail.objects.get(
                                                                                                   order=order.first())]
        return order, order_detail

    def create_orderitem(self, order, order_detail, product):
        item = OrderItem(order=order, order_detail=order_detail, product=product, count=1)
        item.save()

    #
    # def post(self, request, name):
    #
    #     product_obj = Product.objects.filter(name=name)
    #     if product_obj.count() > 0 and product_obj[0].price_on_request:
    #         messages.error(self.request, _('We\'re sorry, we can not add %(article)s to your shopping '
    #                                        'cart because it can only be ordered using our individual offer form') % {
    #                            'article': name})
    #         error_list = JsonResponse(errors=[Error(419, 'Error')], success=False)
    #         return json_response(code=418, x=error_list.dump(), )
    #     if request.user.is_authenticated:
    #         contact = Contact.objects.filter(user_ptr=request.user)
    #         if contact:
    #             if product_obj.count() > 0 and contact.count() > 0:
    #                 company = contact[0].company
    #                 order = Order.objects.filter(orderdetail__state__isnull=True, company=company)
    #                 if order.count() == 0:
    #                     order, order_detail = Order.create_new_order(request)
    #                 else:
    #                     order = order[0]
    #                 order_detail = OrderDetail.objects.get(order=order)
    #                 stock_sufficient, _ = product_obj[0].is_stock_sufficient(order)
    #                 if stock_sufficient:
    #                     item = OrderItem(order=order, order_detail=order_detail, product=product_obj[0], count=1)
    #                     item.save()
    #                 else:
    #                     messages.error(self.request, _('We\'re sorry, we can not add %(article)s to your shopping '
    #                                                    'cart because our stocks are insufficient') % {
    #                                        'article': name})
    #                     error_list = JsonResponse(errors=[Error(418, 'Insufficient stock')], success=False)
    #                     return json_response(code=418, x=error_list.dump(), )
    #
    #             return render(request, self.template_name)
    #         else:
    #             error_list = JsonResponse(errors=[Error(417, 'No Account found')], success=False,
    #                                       next_url='/shop/companies/create')
    #             return json_response(code=417, x=error_list.dump(), )
    #     else:
    #         if product_obj.count() > 0:
    #
    #             order = Order.objects.filter(is_send=False, session=request.session.session_key)
    #             if order.count() == 0:
    #                 order, order_detail = Order.create_new_order(request)
    #             else:
    #                 order = order[0]
    #                 order_detail = OrderDetail.objects.get(order=order)
    #
    #             item = OrderItem(order=order, order_detail=order_detail, product=product_obj[0], count=1)
    #             item.save()
    #
    #         return render(request, self.template_name)


class DeliveryView(TemplateView):
    template_name = 'shop/shoppingcart/shoppingcart-delivery.html'

    def get_context_data(self, **kwargs):
        context = super(DeliveryView, self).get_context_data(**kwargs)
        orders = Order.objects.filter(order_hash=kwargs['uuid'], is_send=False)
        if orders.count() > 0:
            order = orders[0]
            sub_order_items = OrderItem.objects.filter(order=order)
            sub_products_once_only = get_subproducts_once_only(order)
            return {**context, **{'order_details': order, 'sub_products_once_only': sub_products_once_only}}
        else:
            return context


def create_form(request, all_forms, key, value, **kwargs):
    item_builder = ItemBuilder()
    order_item = item_builder.build(key, value)

    if order_item:
        form = create_order_item(order_item=order_item, request=request)
        if form:
            all_forms.setdefault("{}-{}{}".format(order_item.get("order_item"), order_item['product'],
                                                  '-{}'.format(kwargs.get('index')) if kwargs.get(
                                                      'index') and kwargs.get(
                                                      'index') > 0 else ''), form)
        return form


def create_order_item(order_item, request):
    item_type = order_item.pop('product_type')
    form = SubItemForm(item_type, order_item, request)
    return form


def get_subproducts(order):
    order_items = OrderItem.objects.filter(order=order, product__id__in=Product.objects.all())
    assigned_sub_products = order_items.values('product')
    assigned_sub_products = Product.objects.filter(id__in=assigned_sub_products)
    sub_products_once_only = ProductSubItem.objects.filter(
        id__in=assigned_sub_products.values('assigned_sub_products')
    )
    return sub_products_once_only


def get_subproducts_once_only(order):
    sub_products_once_only = get_subproducts(order)
    sub_products_once_only = sub_products_once_only.filter(is_required=True, is_once_per_order=True)
    return sub_products_once_only


class OrderConfirmedView(View):
    template_name = 'shop/shoppingcart/shoppingcart-order-confirmed.html'

    def get(self, request, order):
        _order = Order.objects.get(order_hash=order)
        order_detail = OrderDetail.objects.get(order=_order.id)
        order_detail.date_bill = datetime.now()

        if not order_detail.state:
            order_detail.state = OrderState.objects.get(initial=True)
        order_detail.save()
        if _order.is_send:
            return redirect(reverse("detail_order", args=[order]))
        else:
            _order.is_send = True
            _order.save()
            return render(request, self.template_name, {'order': _order})

    def post(self, request, order):
        _order = Order.objects.get(order_hash=order)
        _order.is_send = True

        _order.save()
        return render(request, self.template_name, {'order': _order})
