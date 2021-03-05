import django_filters
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from cms.models.models import Section, Page
from management.models.models import Header, Footer
from shipping.models import Package, Shipment
from shop.models.orders import OrderDetail
from shop.models.products import ProductCategory, ProductSubItem, FileSubItem, Product
from shop.models.accounts import Contact


class OrderDetailFilter(django_filters.FilterSet):
    free_field_filter = django_filters.CharFilter(field_name="free_field_filter", label=_('Search orders'),
                                                  method='custom_field_filter')

    class Meta:
        model = OrderDetail
        fields = ['state']

    def custom_field_filter(self, queryset, name, value):
        if value.isdigit():
            return queryset.filter(Q(date_added__year=value) |
                                   Q(date_added__month=value))
        else:
            return queryset.filter(
                Q(orderitem__product__name__icontains=value) |
                Q(order__uuid__icontains=value)
            )


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ['category', 'attributes']


class ProductSubItemFilter(django_filters.FilterSet):
    class Meta:
        model = ProductSubItem
        fields = ['id', 'name', 'price']


class FileSubItemFilter(django_filters.FilterSet):
    class Meta:
        model = FileSubItem
        fields = []


class ContactFilter(django_filters.FilterSet):
    free_field_filter = django_filters.CharFilter(field_name="free_field_filter", label=_('Search contacts'),
                                                  method='custom_field_filter')

    type = django_filters.ChoiceFilter(field_name="type", label=_('By type'),
                                       choices=(('anonymous', 'Anonymous Only'),
                                                ('registered', 'Registered Only')),
                                       method='filter_by_type',
                                       initial="registered")

    class Meta:
        model = Contact
        fields = ['company', ]

    def custom_field_filter(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value)|
            Q(last_name__icontains=value)
        )

    def filter_by_type(self, queryset, name, value):
        return queryset.filter(groups__name__in=['client','client supervisor']) if value == 'registered' else \
            queryset.exclude(groups__name__in=['client','client supervisor','staff']).filter(is_superuser=False)


class ProductCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = ProductCategory
        fields = ['mother_category']


class PageFilter(django_filters.FilterSet):
    class Meta:
        model = Page
        fields = ['is_enabled']


class SectionFilter(django_filters.FilterSet):
    class Meta:
        model = Section
        fields = ['page']


class ShipmentPackageFilter(django_filters.FilterSet):
    class Meta:
        model = Package
        fields = ['shipper']


class HeaderFilter(django_filters.FilterSet):
    class Meta:
        model = Header
        fields = ['is_enabled', 'layout']


class FooterFilter(django_filters.FilterSet):
    class Meta:
        model = Footer
        fields = ['is_enabled', 'layout']


class ShipmentFilter(django_filters.FilterSet):
    class Meta:
        model = Shipment
        fields = []
