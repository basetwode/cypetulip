import django_filters

from shop.models import OrderDetail


class OrderDetailFilter(django_filters.FilterSet):
    class Meta:
        model = OrderDetail
        fields = ['state', 'contact']
