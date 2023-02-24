import json

from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.core import serializers
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django_filters.views import FilterView

from billing.utils import calculate_sum
from permissions.error_handler import raise_401
from permissions.views.mixins import PermissionPostGetRequiredMixin, LoginRequiredMixin, PermissionOwnsObjectMixin
from shop.filters.filters import OrderDetailFilter
from shop.forms.account_forms import CompanyForm, ContactForm
from shop.models.accounts import Company, Contact, Address
from shop.models.orders import OrderDetail, OrderItem
from shop.models.products import Product
from shop.utils import get_orderitems_once_only
from shop.utils import json_response
from utils.mixins import PaginatedFilterViews, APIMixin


class OrderDetailView(PermissionOwnsObjectMixin, APIMixin, DetailView):
    model = OrderDetail
    slug_field = "uuid"
    slug_url_kwarg = "order"
    field_name = "contact"
    template_name = 'shop/account/account-order-detail.html'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)

        order_details = self.object

        order_items = OrderItem.objects.filter(order_detail=self.object, order_item__isnull=True,
                                               product__in=Product.objects.all())
        total_without_tax = calculate_sum(order_items)
        total_with_tax = calculate_sum(order_items, True)

        context = {**context, **{
              'total': total_with_tax,
              'total_without_tax': total_without_tax,
              'tax': round(total_with_tax - total_without_tax, 2),
              'order_detail': order_details, 'contact': order_details.contact,
              'order_items': order_items,
              'order_items_once_only': get_orderitems_once_only(self.object)}}

        return context



class OrdersView(LoginRequiredMixin, PermissionPostGetRequiredMixin,  PaginatedFilterViews, FilterView):
    permission_get_required = ['shop.view_orders']
    model = OrderDetail
    template_name = 'shop/account/account-order-overview.html'
    paginate_by = 20
    filterset_class = OrderDetailFilter

    def get_context_data(self, *, object_list=None, **kwargs):
        contact = Contact.objects.get(user_ptr=self.request.user)
        context = super(OrdersView, self).get_context_data(**kwargs)
        return {**context, **{'contact': contact}}

    def get_queryset(self):
        contact = Contact.objects.get(user_ptr=self.request.user)
        return super(OrdersView, self).get_queryset().filter(state__isnull=False, company=contact.company) \
            .order_by('-date_added')


class MyAccountView(LoginRequiredMixin, PermissionPostGetRequiredMixin, TemplateView):
    permission_get_required = ['shop.view_my_account']
    template_name = 'shop/account/account.html'


class AccountSettingsView(LoginRequiredMixin, PermissionPostGetRequiredMixin, UpdateView):
    permission_get_required = ['shop.view_contact']
    permission_post_required = ['shop.change_contact']
    template_name = 'shop/account/account-settings.html'
    model = Contact
    form_class = ContactForm
    context_object_name = 'contact'
    success_url = reverse_lazy('shop:account_settings')

    def form_valid(self, form):
        contact = form.save(commit=False)
        contact.email = contact.username
        return super(AccountSettingsView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        return {**{'next_url': 'shop:account_settings', 'title': 'Account Settings'},
                **super(AccountSettingsView, self).get_context_data(**kwargs)}

    def get_object(self, queryset=None):
        return Contact.objects.get(user_ptr=self.request.user)


class CompanySettingsView(LoginRequiredMixin, PermissionPostGetRequiredMixin, UpdateView):
    permission_get_required = ['shop.view_company']
    permission_post_required = ['shop.change_company']
    template_name = 'shop/account/account-settings.html'
    model = Company
    form_class = CompanyForm
    context_object_name = 'company'
    success_url = reverse_lazy('shop:company_settings')

    def get_context_data(self, **kwargs):
        return {**{'title': 'Company Settings', 'contact': self.request.user.contact,
                   'next_url': 'shop:company_settings'},
                **super(CompanySettingsView, self).get_context_data(**kwargs)}

    def get_object(self, queryset=None):
        return Company.objects.get(contact=self.request.user)


class SearchCustomers(View):
    # todo refactor to rest view
    def get(self, request):
        if 'search' in request.GET and request.user.is_staff:
            search = request.GET.get('search')
            _customers = Contact.objects.filter(Q(email__contains=search) |
                                                Q(company__name__icontains=search) |
                                                Q(username__icontains=search) |
                                                Q(first_name__icontains=search) |
                                                Q(last_name__icontains=search)).distinct()
            _json = json.loads(
                serializers.serialize('json', _customers.all(), use_natural_foreign_keys=True,
                                      use_natural_primary_keys=True))
            return json_response(code=200, x=_json)
        return raise_401(request)


class SearchOrders(View):
    pass # todo Legacy view, ansgar refactors this into rest api. please remove this code afterwards
    # def get(self, request):
    #     _orders, search = SearchOrders.filter_orders(request)
    #     _json = json.loads(
    #         serializers.serialize('json', _orders.all(), use_natural_foreign_keys=True, use_natural_primary_keys=True))
    #     return json_response(code=200, x=_json)
    #
    # @staticmethod
    # def filter_orders(request, admin=False):
    #     if request.user.is_staff or admin:
    #         _orders = Order.objects.filter(orderdetail__state__isnull=False)
    #     else:
    #         contact = Contact.objects.get(user_ptr=request.user)
    #         if contact:
    #             company = contact.company
    #             if company:
    #                 _orders = Order.objects.filter(company=company, orderdetail__state__isnull=False)
    #             else:
    #                 return redirect('/shop/companies/create')
    #         else:
    #             return redirect('/shop/register')
    #     _orders_copy = _orders
    #     search = None
    #     if 'search' in request.GET:
    #         search = request.GET.get('search')
    #         _orders = _orders_copy.filter(Q(uuid__icontains=search) |
    #                                       Q(orderitem__product__name__icontains=search) |
    #                                       Q(orderdetail__uuid__icontains=search)).distinct()
    #         if search.isdigit():
    #             _orders = _orders_copy.filter(Q(orderdetail__date_added__year=search) |
    #                                           Q(orderdetail__date_added__month=search))
    #
    #     return _orders.order_by('-orderdetail__date_added'), search


class AddressOverviewView(PermissionPostGetRequiredMixin, ListView):
    permission_get_required = ['shop.view_address']

    template_name = 'shop/account/account-address-overview.html'
    context_object_name = 'address'
    model = Address

    def get(self, request, *args, **kwargs):
        contact = Contact.objects.get(user_ptr=self.request.user)
        addresses = Address.objects.filter(contact__in=contact.company.contact_set.all())
        return render(request, self.template_name, {'address': addresses, 'contact': contact})


class AddressCreationView(PermissionPostGetRequiredMixin, CreateView):
    permission_get_required = ['shop.add_address']
    permission_post_required = ['shop.add_address']

    template_name = 'shop/generic/generic-create.html'
    context_object_name = 'address'
    model = Address
    fields = ['name','street','number','zipcode','city',]

    def get_success_url(self):
        return reverse_lazy('shop:address_overview')

    def form_valid(self, form):
        address = form.save(commit=False)
        address.contact = Contact.objects.get(user_ptr=self.request.user.id)
        return super(AddressCreationView, self).form_valid(form)


class AddressEditView(PermissionPostGetRequiredMixin, UpdateView):
    permission_get_required = ['shop.view_address']
    permission_post_required = ['shop.change_address']
    field_name = "contact"
    template_name = 'shop/generic/generic-edit.html'
    context_object_name = 'address'
    model = Address
    fields = ['name','street','number','zipcode','city',]

    address_id = None
    slug_field = 'id'
    slug_url_kwarg = 'address_id'

    def get_success_url(self):
        return reverse_lazy('shop:address_overview')


class AddressDeleteView(PermissionPostGetRequiredMixin, DeleteView):
    permission_get_required = ['shop.delete_address']
    permission_post_required = ['shop.delete_address']
    model = Address
    field_name = "contact"
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse_lazy('shop:address_overview')


class PasswordChangeViewCustomer(PasswordChangeView):
    def get_success_url(self):
        messages.success(self.request, _("Password changed!"))
        return reverse_lazy('shop:my_account')


class OrderCancelView(UpdateView):
    model = OrderDetail
    slug_url_kwarg = 'order'
    slug_field = 'uuid'
    fields = []

    def get_success_url(self):
        messages.success(self.request, _("Order canceled!"))
        return reverse_lazy('shop:detail_order', kwargs={'order': self.object.uuid})

    def form_valid(self, form):
        resp = super(OrderCancelView, self).form_valid(form)
        if self.object.state.initial:
            self.object.state = self.object.state.cancel_order_state
        else:
            if self.request.user.is_staff and self.object.state != self.object.state.cancel_order_state:
                self.object.state = self.object.state.cancel_order_state
        self.object.save()
        return resp
