import django_filters
from django.utils.translation import ugettext_lazy as _

from shop.models import OrderDetail


class OrderDetailFilter(django_filters.FilterSet):
    date_added = django_filters.DateFromToRangeFilter(label='Date (Between)')

    type = django_filters.ChoiceFilter(field_name="type", label=_('By type'),
                                       choices=(('all_orders_wo_cart', 'All orders (without carts)'),
                                                ('all_orders', 'All orders'),
                                                ('shopping_carts', 'Shoppingcarts only')),
                                       method='filter_by_type',
                                       initial="all_orders_wo_cart")

    class Meta:
        model = OrderDetail
        fields = ['state', 'date_added']

    def filter_by_type(self, queryset, name, value):
        return queryset.filter(state__isnull=False) if value == 'all_orders_wo_cart' else \
            queryset.filter(state__isnull=True) if value == 'shopping_carts' else \
                queryset
