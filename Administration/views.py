from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View

from Permissions.permissions import check_serve_perms
from Shop.models import Contact, Order
from Shop.my_account.views import SearchOrders


class AdminView(View):

    template_name = 'administration.html'

    def get(self, request):
        contact = Contact.objects.filter(user=request.user)
        company = contact[0].company
        return render(request, self.template_name, {'contact': contact})

    def post(self, request):
        pass

class AdminOrderView(View):

    template_name = 'admin_orders.html'

    def get(self, request, number_of_orders, page=1):
        contact = Contact.objects.get(user=request.user)
        _orders, search = SearchOrders.filter_orders(request,True)
        number_of_orders = '5' if number_of_orders is None else number_of_orders
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
                      {'orders': _orders, 'number_of_orders': number_of_orders, 'contact': contact, 'search': search})

    @check_serve_perms
    def post(self, request):
        pass



class SettingsView(View):

    def get(self, request):
        # <view logic>
        return HttpResponse('SettingsView')

    def post(self, request):
        # <view logic>
        return HttpResponse('result')


class SettingsDetailView(View):
    app_name = None

    def get(self, request, app_name):
        # <view logic>
        return HttpResponse('SettingsDetailView')

    def post(self, request):
        # <view logic>
        return HttpResponse('result')

    def get_app(self, queryset=None):
        return queryset.get(app_name=self.app_name)