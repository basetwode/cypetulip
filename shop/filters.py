import django_filters

from cms.models import Section, Page
from shipping.models import Package
from shop.models import OrderDetail, Product, Contact, ProductCategory, FileSubItem


class OrderDetailFilter(django_filters.FilterSet):
    class Meta:
        model = OrderDetail
        fields = ['state', 'contact']


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ['category', 'attributes']


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
