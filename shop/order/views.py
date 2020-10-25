from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View
from django.utils.translation import gettext as _

from shop.errors import JsonResponse, Error, FieldError
from shop.models import (Contact, Order, OrderDetail, OrderItem,
                         Product)

__author__ = 'Anselm'

from shop.utils import json_response


class ShoppingCartView(View):
    template_name = 'order/shopping-cart-nav.html'

    def post(self, request, product):

        product_obj = Product.objects.filter(name=product)
        if request.user.is_authenticated:
            contact = Contact.objects.filter(user=request.user)
            if contact:
                if product_obj.count() > 0 and contact.count() > 0:
                    company = contact[0].company
                    order = Order.objects.filter(is_send=False, company=company)
                    if order.count() == 0:
                        order = Order(is_send=False, company=company)
                        order.save()
                        order_detail = OrderDetail(order=order, order_number=order.order_hash,
                                                   contact=contact[0])
                        order_detail.save()
                    else:
                        order = order[0]
                    if self.is_stock_sufficient(order, product_obj[0]):
                        item = OrderItem(order=order, product=product_obj[0], count=1)
                        item.save()
                    else:
                        messages.error(self.request, _('Were sorry, we can not add %(article)s to your shopping '
                                                       'cart because our stocks are insufficient') % {'article': product})
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
                    order = Order(is_send=False, session=request.session.session_key)
                    order.save()
                    order_detail = OrderDetail(order=order, order_number=order.order_hash)
                    order_detail.save()
                else:
                    order = order[0]

                item = OrderItem(order=order, product=product_obj[0], count=1)
                item.save()

            return render(request, self.template_name)

    def is_stock_sufficient(self, order, product):
        order_items_count_with_product = order.orderitem_set.filter(product=product).count()
        return 0 < product.stock > order_items_count_with_product

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
            contact = Contact.objects.filter(user=request.user)
            if contact:
                company = contact[0].company
                order = Order.objects.filter(is_send=False, company=company)
                if order.count() == 0:
                    order = ['']
                return render(request, self.template_name, {'order_details': order[0]})
            return redirect('/cms/home')
        else:
            order = Order.objects.filter(is_send=False, session=request.session.session_key)
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
            return json_response(200, x={'next_url': ''})
        else:
            # return json_response(code=400, x={'success': False,
            #                                   'errors': [([(formkey, v[0]) for k, v in form.errors.items()]) for
            #                                              formkey, form
            #                                              in forms.items()]
            #                                   })
            errors = []
            for formkey, form in forms.items():
                errors_form = [FieldError(message=v[0], field_name=formkey) for k, v in form.errors.items()]
                errors.extend(errors_form)

            # errors = [[FieldError(message=v[0], field_name=k) for k, v in form.errors.items()] for
            #           formkey, form
            #           in forms.items()]

            result = json_response(code=400, x=JsonResponse(success=False, errors=errors).dump())
            return result
