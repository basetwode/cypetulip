import json

from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView

from permissions.permissions import check_serve_perms
from shop.models import Contact, Order, OrderItem, Product, OrderDetail, Address
from shop.my_account.forms import CompanyForm, ContactForm
from shop.order.utils import get_orderitems_once_only
from shop.utils import json_response


class OrderDetailView(View):
    template_name = 'my_account/orders-detail.html'

    @check_serve_perms
    def get(self, request, order):
        contact = Contact.objects.filter(user=request.user)
        if contact:
            _order = Order.objects.get(order_hash=order)
            order_details = OrderDetail.objects.get(order_number=order)
            if _order:
                total = 0
                for order_item in _order.orderitem_set.all():
                    total += order_item.product.price
                _order.total = total
                order_items = OrderItem.objects.filter(order=_order, order_item__isnull=True,
                                                       product__in=Product.objects.all())
                return render(request, self.template_name,
                              {'order_details': order_details, 'order': _order, 'contact': contact,
                               'order_items': order_items,
                               'order_items_once_only': get_orderitems_once_only(_order)})
            else:
                return redirect('/shop/register')

    def post(self, request):
        pass


class OrdersView(View):
    template_name = 'my_account/orders.html'

    @check_serve_perms
    def get(self, request, page=1, **kwargs):
        contact = Contact.objects.filter(user=request.user)
        if contact:
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
        else:
            return redirect('/shop/register')

    @check_serve_perms
    def post(self, request):
        pass


class MyAccountView(View):
    template_name = 'my_account/my-account.html'

    @check_serve_perms
    def get(self, request):

        contact = Contact.objects.filter(user=request.user)
        if contact:
            return render(request, self.template_name, {'contact': contact})
        else:
            return redirect('/shop/register')

    @check_serve_perms
    def post(self, request):
        pass


class AccountSettingsView(View):
    template_name = 'my_account/settings.html'

    @check_serve_perms
    def get(self, request):
        contact = Contact.objects.get(user=request.user)
        if contact:
            form = ContactForm(instance=contact)
            return render(request, self.template_name, {'contact': contact, 'form': form, 'title': 'Account Settings',
                                                        'next_url': 'account_settings'})
        else:
            return redirect('/shop/register')

    @check_serve_perms
    def post(self, request):
        contact = Contact.objects.filter(user=request.user)
        form = ContactForm(request.POST, instance=contact)
        form.save()
        return render(request, self.template_name, {'contact': contact, 'form': form, 'title': 'Account Settings',
                                                    'next_url': 'account_settings'})


class CompanySettingsView(View):
    template_name = 'settings-details.html'

    @check_serve_perms
    def get(self, request):
        contact = Contact.objects.get(user=request.user)
        if contact:
            company = contact.company
            if company:
                form = CompanyForm(instance=company)
                return render(request, self.template_name, {'contact': contact, 'form': form,
                                                            'title': 'Company Settings',
                                                            'next_url': 'company_settings'})
            else:
                return redirect('/shop/companies/create')
        else:
            return redirect('/shop/register')


@check_serve_perms
def post(self, request):
    contact = Contact.objects.filter(user=request.user)
    company = contact.company
    form = CompanyForm(request.POST, files=request.FILES, instance=company)
    form.save()
    return render(request, self.template_name, {'contact': contact, 'form': form, 'title': 'Company Settings',
                                                'next_url': 'company_settings'})


class SearchOrders(View):

    def get(self, request):
        _orders, search = SearchOrders.filter_orders(request)
        _json = json.loads(
            serializers.serialize('json', _orders.all(), use_natural_foreign_keys=True, use_natural_primary_keys=True))
        return json_response(code=200, x=_json)

    @staticmethod
    def filter_orders(request, admin=False):
        if request.user.is_staff or admin:
            _orders = Order.objects.filter(is_send=True)
        else:
            contact = Contact.objects.filter(user=request.user)
            if contact:
                company = contact.company
                if company:
                    _orders = Order.objects.filter(is_send=True, company=company)
                else:
                    return redirect('/shop/companies/create')
            else:
                return redirect('/shop/register')

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

        return _orders.order_by('-orderdetail__date_added'), search


class AddressOverviewView(ListView):
    template_name = 'my_account/address-overview.html'
    context_object_name = 'address'
    model = Address


class AddressCreationView(CreateView):
    template_name = 'generic-create.html'
    context_object_name = 'address'
    model = Address
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('address_overview')


class AddressEditView(UpdateView):
    template_name = 'generic-edit.html'
    context_object_name = 'address'
    model = Address
    fields = '__all__'

    address_id = None
    slug_field = 'id'
    slug_url_kwarg = 'address_id'

    def get_success_url(self):
        return reverse_lazy('address_overview')


class AddressDeleteView(DeleteView):
    model = Address
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('address_overview')
