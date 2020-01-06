import json

from django.core import serializers
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import View

from permissions.permissions import check_serve_perms
from shop.models import Contact, Order, Product, OrderItem
from shop.my_account.forms import ContactForm, CompanyForm
from shop.order.utils import get_orderitems_once_only
from shop.utils import json_response


class OrderDetailView(View):
    template_name = 'my_account/orders_detail.html'

    @check_serve_perms
    def get(self, request, order):
        contact = Contact.objects.get(user=request.user)
        company = contact.company
        _order = Order.objects.get(order_hash=order)
        if _order:
            total = 0
            for order_item in _order.orderitem_set.all():
                total += order_item.product.price
            _order.total = total
            order_items = OrderItem.objects.filter(order=_order, order_item__isnull=True,product__in=Product.objects.all())
            return render(request, self.template_name, {'order_details': _order,'order': _order,'contact':contact,
                                                        'order_items': order_items,
                                                        'order_items_once_only': get_orderitems_once_only(_order)})


    def post(self, request):
        pass


class OrdersView(View):
    template_name = 'my_account/orders.html'

    @check_serve_perms
    def get(self, request, page=1):
        contact = Contact.objects.get(user=request.user)
        _orders, search = SearchOrders.filter_orders(request)
        number_of_orders = '5'
        paginator = Paginator(_orders, number_of_orders)
        for order in _orders:
            total = 0
            for order_item in order.orderitem_set.all():
                total += order_item.product.price
            order.total = total
        try:
            _orders = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            _orders = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            _orders = paginator.page(paginator.num_pages)
        return render(request, self.template_name,
                      {'orders': _orders, 'contact': contact, 'search': search})

    @check_serve_perms
    def post(self, request):
        pass


class MyAccountView(View):
    template_name = 'my_account/my_account.html'

    @check_serve_perms
    def get(self, request):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        return render(request, self.template_name, {'contact': contact})

    @check_serve_perms
    def post(self, request):
        pass


class AccountSettingsView(View):
    template_name = 'my_account/account_settings.html'

    @check_serve_perms
    def get(self, request):
        contact = Contact.objects.get(user=request.user)
        company = contact.company
        form = ContactForm(instance=contact)
        return render(request, self.template_name, {'contact': contact,'form':form})

    @check_serve_perms
    def post(self, request):
        contact = Contact.objects.get(user=request.user)
        company = contact.company
        form = ContactForm(request.POST,instance=contact)
        form.save()
        return render(request, self.template_name, {'contact': contact,'form':form})

class CompanySettingsView(View):
    template_name = 'my_account/company_settings.html'

    @check_serve_perms
    def get(self, request):
        contact = Contact.objects.get(user=request.user)
        company = contact.company
        form = CompanyForm(instance=company)
        return render(request, self.template_name, {'contact': contact,'form':form})

    @check_serve_perms
    def post(self, request):
        contact = Contact.objects.get(user=request.user)
        company = contact.company
        form = CompanyForm(request.POST,files=request.FILES,instance=company)
        form.save()
        return render(request, self.template_name, {'contact': contact,'form':form})

class SearchOrders(View):

    def get(self, request):
        _orders,search = SearchOrders.filter_orders(request)
        _json = json.loads(serializers.serialize('json',_orders.all(),use_natural_foreign_keys=True, use_natural_primary_keys=True))
        return json_response(code=200,x=_json)


    @staticmethod
    def filter_orders(request, admin=False):
        contact = Contact.objects.get(user=request.user)
        company = contact.company

        _orders = Order.objects.filter(is_send=True, company=company) if not admin else Order.objects.filter(is_send=True)
        _orders_copy = _orders
        search = None
        if 'search' in request.GET:
            search = request.GET.get('search')
            _orders = _orders_copy.filter(Q(order_hash__icontains=search) |
                                          Q(orderitem__product__name__icontains=search) |
                                          Q(orderdetail__order_number__icontains=search)).distinct()
            if search.isdigit():
                _orders = _orders_copy.filter(Q(orderdetail__date_added__year=search) |
                                              Q(orderdetail__date_added__month=search))

        return (_orders.order_by('-orderdetail__date_added'), search)
