import operator
from datetime import datetime
from functools import reduce

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View, ListView, FormView
from django.utils.translation import ugettext_lazy as _


from cms.models import Section
from permissions.error_handler import raise_404
from shop.forms import ProductAttributeForm, IndividualOfferForm
from shop.mixins import TaxView, EmailNotifyStaffView
from shop.models import (Order, OrderDetail, OrderState,
                         Product, ProductCategory, OrderItem, ProductAttributeType, ProductAttributeTypeInstance,
                         Contact)
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


class ProductView(TaxView, ListView):
    template_name = 'products.html'
    context_object_name = 'products'
    paginate_by = 9

    def _get_url_page(self, products_list, page):
        paginator = Paginator(products_list, self.paginate_by)
        try:
            url_list = paginator.page(page)
        except PageNotAnInteger:
            url_list = paginator.page(1)
        except EmptyPage:
            url_list = paginator.page(paginator.num_pages)
        return url_list

    def get_queryset(self):
        selected_category = ProductCategory.objects.filter(name=self.kwargs['category'])
        if selected_category.count() > 0 and selected_category[0].child_categories.all():
            products = Product.objects.filter(is_public=True, category__in=selected_category[0].
                                              child_categories.all())
        else:
            products = Product.objects.filter(is_public=True, category__in=selected_category)
        if not selected_category:
            products = Product.objects.filter(is_public=True)

        product_attribute_categories = ProductAttributeType.objects. \
            filter(productattributetypeinstance__product__in=products).annotate(count=Count('name', distinct=True))
        attribute_form = ProductAttributeForm(product_attribute_categories, self.request.GET)

        attribute_filter = (Q(type__name=k, value=v) for k, v in attribute_form.data.items()) \
            if attribute_form.data else None
        selected_attributes = ProductAttributeTypeInstance.objects.filter(reduce(operator.or_, attribute_filter)) \
            if attribute_filter else []

        for selected_attribute in selected_attributes:
            products = products.filter(attributes__id__in=[selected_attribute.id])

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)

        sections = Section.objects.filter(page__page_name="Products")

        categories = ProductCategory.objects.filter(is_main_category=True)
        products = self.object_list

        product_attribute_categories = ProductAttributeType.objects. \
            filter(productattributetypeinstance__product__in=products).annotate(count=Count('name', distinct=True))
        attribute_form = ProductAttributeForm(product_attribute_categories, self.request.GET)

        # Update available list of attributes
        product_attribute_categories = ProductAttributeType.objects. \
            filter(productattributetypeinstance__product__in=products).annotate(count=Count('name', distinct=True))
        product_attribute_types = ProductAttributeTypeInstance.objects. \
            filter(product__in=products).annotate(count=Count('value', product__in=products))

        products = self._get_url_page(products, self.request.GET.get('page'))

        return {**context, **{'sections': sections, 'products': products,
                          'categories': categories,
                          'types': product_attribute_categories,
                          'type_instances': product_attribute_types,
                          'attribute_form': attribute_form,
                          'selected_category': self.kwargs['category']}}


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
        _order = Order.objects.get(order_hash=order)
        order_detail = OrderDetail.objects.get(order=_order.id)
        order_detail.date_bill = datetime.now()

        for order_item in OrderItem.objects.filter(order=_order):
            order_item.price = order_item.product.special_price if \
                order_item.product.special_price else order_item.product.price
            order_item.save()

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


class IndividualOfferView(EmailNotifyStaffView, FormView):
    form_class = IndividualOfferForm
    template_name = 'order/offer.html'
    success_url = reverse_lazy('shop:products',kwargs={'category': ''})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(name=self.kwargs['product'])
        return context

    def get_initial(self, form_class=None):

        initial = super().get_initial()
        if self.request.user.is_authenticated:
            contact = Contact.objects.get(user=self.request.user)
            initial['mail'] = contact.email
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.request.user.is_authenticated:
            self.object.contact = Contact.objects.get(user=self.request.user)
        self.object.product = Product.objects.get(name=self.kwargs['product'])
        self.object.save()
        self.notify()
        messages.success(self.request, _("Thank you for your request, we'll contact you soon"))
        return HttpResponseRedirect(self.get_success_url())

