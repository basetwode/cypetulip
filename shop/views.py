from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from permissions.error_handler import raise_404
from permissions.permissions import check_serve_perms
from shop.models import (Contact, Order, OrderDetail, OrderState,
                         Product, ProductCategory)


# Create your views here.


class IndexView(View):
    template_name = 'index.html'

    def get(self, request):
        # form = self.form_class(initial=self.initial)
        return render(request, self.template_name)

    def post(self, request):
        # <view logic>
        return HttpResponse('result')


class ProductView(View):
    template_name = 'products.html'

    def get(self, request, category):

        selected_category = ProductCategory.objects.filter(name=category)
        if selected_category.count() > 0 and selected_category[0].child_categories.all():
            products = Product.objects.filter(is_public=True, category__in=selected_category[0].child_categories.all())
        else:
            products = Product.objects.filter(is_public=True, category__in=selected_category)
        if not selected_category:
            products = Product.objects.filter(is_public=True)
        categories = ProductCategory.objects.filter(is_main_category=True)
        # form = self.form_class(initial=self.initial).
        return render(request, self.template_name, {'products': products,
                                                    'categories': categories,
                                                    'selected_category': category})

    def post(self, request):
        # <view logic>
        return HttpResponse('result')


class ProductDetailView(View):
    template_name = 'product-detail.html'

    def get(self, request, product):
        selected_product = Product.objects.filter(is_public=True, name=product)
        categories = ProductCategory.objects.filter(is_main_category=True)
        if selected_product.count() > 0:
            selected_product = selected_product[0]
        else:
            return raise_404(request)
        return render(request, self.template_name, {'product': selected_product,
                                                    'categories': categories})

    def post(self, request):
        # <view logic>
        return HttpResponse('result')


class OrderView(View):
    def get(self, request, product_id, order_step):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name)

    def post(self, request):
        # <view logic>
        return HttpResponse('result')


class OrderConfirmedView(View):
    template_name = 'order/order-confirmed.html'

    @check_serve_perms
    def get(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.get(order_hash=order, is_send=False, company=company)
        _order.is_send = True
        _order.save()
        return render(request, self.template_name, {'order': _order})

    @check_serve_perms
    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.get(order_hash=order, is_send=False, company=company)
        _order.is_send = True
        order_detail = OrderDetail.objects.get(order=_order.id)
        order_detail.state = OrderState.objects.get(initial=True)
        _order.save()
        return render(request, self.template_name, {'order': _order})
