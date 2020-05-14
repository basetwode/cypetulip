from django.shortcuts import render, redirect
from django.views.generic import View

from shop.Errors import JsonResponse, Error
from shop.models import (Contact, Order, OrderDetail, OrderItem,
                         Product)

__author__ = 'Anselm'

from shop.utils import json_response


class ShoppingCartView(View):
    template_name = 'order/shopping-cart-nav.html'

    def post(self, request, product):
        if request.user.is_authenticated:
            product_obj = Product.objects.filter(name=product)
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

                    item = OrderItem(order=order, product=product_obj[0], count=1)
                    item.save()

                return render(request, self.template_name)
            else:
                error_list = JsonResponse(errors=[Error(417, 'No Account found')], success=False,
                                          next_url='/shop/companies/create')
                return json_response(code=417, x=error_list.dump(), )
        else:
            error_list = JsonResponse(errors=[Error(417, 'No Account found')], success=False,
                                      next_url='/shop/register')
            return json_response(code=417, x=error_list.dump(), )


class ShoppingCartDetailView(View):
    template_name = 'order/shopping-cart-detail.html'

    def delete(self, request, product_id):
        if request.user.is_authenticated:
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

    def post(self, request):
        pass
