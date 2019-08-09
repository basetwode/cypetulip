from django.shortcuts import render
from django.utils.translation import ungettext_lazy
from django.views.generic import View
from Shop.models import Contact, OrderDetail, Order, Product, Company, OrderItem

__author__ = 'Anselm'



class ShoppingCartView(View):

    template_name = 'order/shopping_cart.html'

    def get(self, request, product):
        if request.user.is_authenticated:
            return render(request, self.template_name)

    def post(self, request, product):
        # <view logic>
        if request.user.is_authenticated:
            product_obj = Product.objects.filter(name=product)
            contact = Contact.objects.filter(user=request.user)


            if product_obj.count() > 0 and contact.count()>0:
                company = contact[0].company
                order = Order.objects.filter(is_send=False,company=company)
                if order.count()==0:
                    order = Order(is_send=False, company=company)
                    order.save()
                    order_detail = OrderDetail(order=order,order_number=order.order_hash,
                                               contact = contact[0])
                    order_detail.save()
                else:
                    order = order[0]

                item = OrderItem(order=order,product=product_obj[0],count=1)
                item.save()

            return render(request, self.template_name)


class ShoppingCartDetailView(View):

    template_name = 'order/shopping_cart_detail.html'

    def get(self, request):
        if request.user.is_authenticated:
            contact = Contact.objects.filter(user=request.user)
            company = contact[0].company
            order = Order.objects.filter(is_send=False,company=company)
            if order.count()==0:
                order = ['']
            return render(request, self.template_name, {'order_details':order[0]})

    def post(self, request):
        pass
