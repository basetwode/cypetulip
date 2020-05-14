from datetime import datetime

from django.db.models import When, FloatField, Case, Count, F
from django.db.models.functions import Round
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from permissions.error_handler import raise_404
from shop.forms import ProductAttributeForm
from shop.models import (Contact, Order, OrderDetail, OrderState,
                         Product, ProductCategory, OrderItem, ProductAttributeType, ProductAttributeTypeInstance)
# Create your views here.
from shop.utils import json_response


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

        product_attribute_categories = ProductAttributeType.objects. \
            filter(productattributetypeinstance__product__in=products).annotate(count=Count('name', distinct=True))
        attribute_form = ProductAttributeForm(product_attribute_categories, request.GET)

        selected_attribute_types = ProductAttributeType.objects.filter(name__in=attribute_form.data)
        selected_attributes = ProductAttributeTypeInstance.objects.filter(type__in=selected_attribute_types). \
            filter(value__in=attribute_form.data.values())

        for selected_attribute in selected_attributes:
            products = products.filter(attributes__id=selected_attribute.id)

        # Update available list of attributes
        product_attribute_categories = ProductAttributeType.objects. \
            filter(productattributetypeinstance__product__in=products).annotate(count=Count('name', distinct=True))
        product_attribute_types = ProductAttributeTypeInstance.objects. \
            filter(product__in=products).annotate(count=Count('value', product__in=products))

        self.add_tax_to_product(products)

        return render(request, self.template_name, {'products': products,
                                                    'categories': categories,
                                                    'types': product_attribute_categories,
                                                    'type_instances': product_attribute_types,
                                                    'attribute_form': attribute_form,
                                                    'selected_category': category})

    def post(self, request):
        # <view logic>
        return HttpResponse('result')

    @staticmethod
    def add_tax_to_product(products):
        products.annotate(tprice=Round((Case(
            When(special_price=False, then='price'),
            When(special_price__gte=0, then='special_price'),
            default='price',
            output_field=FloatField(),
        ) * (F('tax') + 1), FloatField(), 2)))


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

    def get(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.get(order_hash=order, company=company)
        order_detail = OrderDetail.objects.get(order=_order.id)
        order_detail.date_bill = datetime.now()

        for order_item in OrderItem.objects.filter(order=_order):
            order_item.price = order_item.product.special_price if \
                order_item.product.special_price else order_item.product.price
            order_item.save()

        order_detail.state = OrderState.objects.get(initial=True)
        order_detail.save()
        if _order.is_send:
            return redirect(reverse("detail_order", args=[order]))
        else:
            _order.is_send = True
            _order.save()
            return render(request, self.template_name, {'order': _order})

    def post(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        _order = Order.objects.get(order_hash=order, is_send=False, company=company)
        _order.is_send = True

        _order.save()
        return render(request, self.template_name, {'order': _order})


class OrderCancelView(View):
    def post(self, request, order_hash):
        _order = OrderDetail.objects.get(order_number=order_hash)
        if _order.state.initial:
            _order.state = _order.state.cancel_order_state
        else:
            if request.user.is_staff and _order.state != _order.state.cancel_order_state:
                _order.state = _order.state.cancel_order_state
            else:
                return json_response(500, x={})
        try:
            _order.save()
            return redirect(request.META.get('HTTP_REFERER'))
        except:
            return json_response(500, x={})
