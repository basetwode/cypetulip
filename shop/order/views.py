from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import View

from shop.errors import Error, FieldError
from shop.errors import JsonResponse
from shop.models import Contact, Order, OrderItem, Product, ProductSubItem
from shop.order.forms import ItemBuilder, SubItemForm, OrderDetail
from shop.utils import json_response

__author__ = 'Anselm'


class ShoppingCartView(View):
    template_name = 'order/shopping-cart-nav.html'

    def post(self, request, product):

        product_obj = Product.objects.filter(name=product)
        if product_obj.count() > 0 and product_obj[0].price_on_request:
            messages.error(self.request, _('We\'re sorry, we can not add %(article)s to your shopping '
                                           'cart because it can only be ordered using our individual offer form') % {
                               'article': product})
            error_list = JsonResponse(errors=[Error(419, 'Error')], success=False)
            return json_response(code=418, x=error_list.dump(), )
        if request.user.is_authenticated:
            contact = Contact.objects.filter(user_ptr=request.user)
            if contact:
                if product_obj.count() > 0 and contact.count() > 0:
                    company = contact[0].company
                    order = Order.objects.filter(orderdetail__state__isnull=True, company=company)
                    if order.count() == 0:
                        order, order_detail = Order.create_new_order(request)
                    else:
                        order = order[0]
                    order_detail = OrderDetail.objects.get(order=order)
                    stock_sufficient, _ = product_obj[0].is_stock_sufficient(order)
                    if stock_sufficient:
                        item = OrderItem(order=order, order_detail=order_detail, product=product_obj[0], count=1)
                        item.save()
                    else:
                        messages.error(self.request, _('We\'re sorry, we can not add %(article)s to your shopping '
                                                       'cart because our stocks are insufficient') % {
                                           'article': product})
                        error_list = JsonResponse(errors=[Error(418, 'Insufficient stock')], success=False)
                        return json_response(code=418, x=error_list.dump(), )

                return render(request, self.template_name)
            else:
                error_list = JsonResponse(errors=[Error(417, 'No Account found')], success=False,
                                          next_url='/shop/companies/create')
                return json_response(code=417, x=error_list.dump(), )
        else:
            if product_obj.count() > 0:

                order = Order.objects.filter(is_send=False, session=request.session.session_key)
                if order.count() == 0:
                    order, order_detail = Order.create_new_order(request)
                else:
                    order = order[0]
                    order_detail = OrderDetail.objects.get(order=order)

                item = OrderItem(order=order, order_detail=order_detail, product=product_obj[0], count=1)
                item.save()

            return render(request, self.template_name)



class ShoppingCartDetailView(View):
    template_name = 'order/shopping-cart-detail.html'

    def delete(self, request, product_id):
        if request.user.is_authenticated:
            instance = OrderItem.objects.get(id=product_id)
            instance.delete()
        else:
            instance = OrderItem.objects.get(id=product_id)
            instance.delete()
        return render(request, self.template_name)

    def get(self, request):
        if request.user.is_authenticated:
            contact = Contact.objects.filter(user_ptr=request.user)
            if contact:
                company = contact[0].company
                order = Order.objects.filter(orderdetail__state__isnull=True, company=company)
                if order.count() == 0:
                    order = ['']
                return render(request, self.template_name, {'order_details': order[0]})
            return redirect('/cms/home')
        else:
            order = Order.objects.filter(orderdetail__state__isnull=True, session=request.session.session_key)
            if order.count() == 0:
                order = ['']
            return render(request, self.template_name, {'order_details': order[0]})

    def post(self, request):
        forms = {}
        forms_are_valid = True
        for post in request.FILES:
            values = request.FILES.getlist(post)
            file_index = 0
            for value in values:
                form = create_form(request, forms, post, value,
                                   index=file_index)
                file_index += 1
                if form:
                    forms_are_valid = forms_are_valid and form.is_valid()
        for post in request.POST:
            value = request.POST.get(post)
            # TODO this items can also be multiple, check that

            form = create_form(request, forms, post, value)
            if form:
                forms_are_valid = forms_are_valid and form.is_valid()

        if forms_are_valid:
            for k, v in forms.items():
                v.save()
            return json_response(200, x={'next_url': ''})
        else:
            errors = []
            for formkey, form in forms.items():
                errors_form = [FieldError(message=v[0], field_name=formkey) for k, v in form.errors.items()]
                errors.extend(errors_form)
            result = json_response(code=400, x=JsonResponse(success=False, errors=errors).dump())
            return result


class DeliveryView(View):
    template_name = 'order/delivery.html'

    def get(self, request, order):
        orders = Order.objects.filter(order_hash=order, is_send=False)
        if orders.count() > 0:
            order = orders[0]
            sub_order_items = OrderItem.objects.filter(order=order)
            sub_products_once_only = get_subproducts_once_only(order)
            return render(request, self.template_name, {'order_details': order,
                                                        'sub_products_once_only': sub_products_once_only})
        else:
            return redirect(reverse('shop:shopping_cart'))


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
