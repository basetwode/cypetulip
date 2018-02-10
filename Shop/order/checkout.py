import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from Shop.Errors import JsonResponse, FieldError
from Shop.models import Order, Contact, OrderItem, ProductSubItem, Product
from Shop.order.forms import SubItemForm, ItemBuilder
from Shop.utils import create_hash, json_response

__author__ = 'Anselm'


class CheckoutView(View):
    template_name = 'order/checkout.html'

    def get(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        order = Order.objects.filter(order_hash=order, is_send=False, company=company)
        if order.count() > 0:
            order = order[0]
            sub_order_items = OrderItem.objects.filter(order=order).exclude(product__in=Product.objects.all())
            sub_order_items.delete()
            sub_products_once_only = self.get_subproducts_once_only(order)
            return render(request, self.template_name, {'order_details': order,
                                                        'sub_products_once_only': sub_products_once_only})

    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.filter(order_hash=order, is_send=False, company=company)
        if _order.count() > 0:
            forms = {}
            forms_are_valid = True
            for post in request.FILES:
                values = request.FILES.getlist(post)
                file_index = 0
                for value in values:
                    form = self.create_form(request, forms, post, value,
                                            index=file_index)
                    file_index += 1
                    if form:
                        forms_are_valid = forms_are_valid and form.is_valid()
            for post in request.POST:
                value = request.POST.get(post)

                # TODO this items can also be multiple, check that

                form = self.create_form(request, forms, post, value)
                if form:
                    forms_are_valid = forms_are_valid and form.is_valid()

            if forms_are_valid:
                for k, v in forms.items():
                    v.save()
                token = create_hash()
                ord = _order[0]
                ord.token = token
                ord.save()
                result = json_response(code=200, x=JsonResponse(token=token).dump())
                return result
                # return json_response(200, x={'token': token, 'order': _order[0].order_hash})
            else:
                # return json_response(code=400, x={'success': False,
                #                                   'errors': [([(formkey, v[0]) for k, v in form.errors.items()]) for
                #                                              formkey, form
                #                                              in forms.items()]
                #                                   })
                errors=[]
                for formkey, form in forms.items():
                    errors_form = [FieldError(message=v[0], field_name=formkey) for k, v in form.errors.items()]
                    errors.extend(errors_form)

                # errors = [[FieldError(message=v[0], field_name=k) for k, v in form.errors.items()] for
                #           formkey, form
                #           in forms.items()]

                result = json_response(code=400, x=JsonResponse(success=False, errors=errors).dump())
                return result

    def create_form(self, request, all_forms, key, value, **kwargs):
        item_builder = ItemBuilder()
        order_item = item_builder.build(key, value)

        if order_item:
            form = self.create_order_item(order_item=order_item, request=request)
            if form:
                all_forms.setdefault("{}-{}{}".format(order_item.get("order_item"), order_item['product'],
                                                      '-{}'.format(kwargs.get('index')) if kwargs.get(
                                                          'index') and kwargs.get(
                                                          'index') > 0 else ''), form)
            return form

    def create_order_item(self, order_item, request):
        item_type = order_item.pop('product_type')
        form = SubItemForm(item_type, order_item, request)
        return form

    def get_subproducts(self, order):
        order_items = OrderItem.objects.filter(order=order, product__id__in=Product.objects.all())
        assigned_sub_products = order_items.values('product')
        assigned_sub_products = Product.objects.filter(id__in=assigned_sub_products)
        sub_products_once_only = ProductSubItem.objects.filter(
            id__in=assigned_sub_products.values('assigned_sub_products')
        )
        return sub_products_once_only

    def get_subproducts_once_only(self, order):
        sub_products_once_only = self.get_subproducts(order)
        sub_products_once_only = sub_products_once_only.filter(is_required=True, is_once_per_order=True)
        return sub_products_once_only
