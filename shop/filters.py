import django_filters
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from cms.models import Section, Page
from management.models import Header, Footer
from shipping.models import Package
from shop.models import OrderDetail, Product, Contact, ProductCategory, FileSubItem, ProductSubItem


class OrderDetailFilter(django_filters.FilterSet):
    free_field_filter = django_filters.CharFilter(field_name="free_field_filter", label=_('Search orders'),
                                                  method='custom_field_filter')

    class Meta:
        model = OrderDetail
        fields = ['state', ]

    def custom_field_filter(self, queryset, name, value):
        if value.isdigit():
            return queryset.filter(Q(date_added__year=value) |
                                   Q(date_added__month=value))
        else:
            return queryset.filter(
                Q(orderitem__product__name__icontains=value) |
                Q(order__order_hash__icontains=value)
            )


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ['category', 'attributes']


class ProductSubItemFilter(django_filters.FilterSet):
    class Meta:
        model = ProductSubItem
        fields = []


class FileSubItemFilter(django_filters.FilterSet):
    class Meta:
        model = FileSubItem
        fields = []


class ContactFilter(django_filters.FilterSet):
    class Meta:
        model = Contact
        fields = ['company']


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
