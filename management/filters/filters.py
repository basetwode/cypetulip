import django_filters
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from shop.models.orders import Discount, OrderDetail


class OrderDetailFilter(django_filters.FilterSet):
    date_added = django_filters.DateFromToRangeFilter(label='Date (Between)')
    free_field_filter = django_filters.CharFilter(field_name="free_field_filter", label=_('Search orders'),
                                                  method='custom_field_filter')

    class Meta:
        model = OrderDetail
        fields = ['state', 'contact']

    def custom_field_filter(self, queryset, name, value):
        if value.isdigit():
            return queryset.filter(Q(date_added__year=value) |
                                   Q(date_added__month=value))
        else:
            return queryset.filter(
                Q(orderitem__product__name__icontains=value) |
                Q(order__uuid__icontains=value) |
                Q(contact__last_name__icontains=value) |
                Q(contact__first_name__icontains=value) |
                Q(contact__company__name__icontains=value) |
                Q(contact__email__icontains=value)
            )


class DiscountFilter(django_filters.FilterSet):
    class Meta:
        model = Discount
        fields = ['enabled']
