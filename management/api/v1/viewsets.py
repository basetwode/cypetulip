import django_filters
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser

from management.api.v1.serializers import OrderDetailSerializer, CompanySerializer, ProductSerializer, \
    ProductCategorySerializer, ProductAttributeTypeSerializer, \
    ProductAttributeTypeInstanceSerializer, ProductSubItemSerializer, ProductImageSerializer, OrderStateSerializer, \
    PaymentDetailSerializer, PaymentMethodSerializer
from payment.models import PaymentDetail, PaymentMethod, Payment
from shop.models import Product, ProductCategory, ProductAttributeType, ProductAttributeTypeInstance, ProductSubItem, \
    ProductImage, Company, OrderDetail, OrderState
from shop.utils import create_hash


class OrderDetailAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_queryset(self):
        queryset = OrderDetail.objects.all()
        order_hash = self.request.query_params.get('orderHash', None)
        order_year = self.request.query_params.get('orderYear', None)
        if order_hash is not None:
            return queryset.filter(order__order_hash=order_hash)
        if order_year is not None:
            return queryset.filter(date_bill__year=order_year)
        else:
            return super(OrderDetailAdmViewSet, self).get_queryset()


class CompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductAttributeTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductAttributeType.objects.all()
    serializer_class = ProductAttributeTypeSerializer


class ProductAttributeTypeInstanceViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductAttributeTypeInstance.objects.all()
    serializer_class = ProductAttributeTypeInstanceSerializer


class ProductSubItemViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductSubItem.objects.all()
    serializer_class = ProductSubItemSerializer


class ProductImageViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class ProductImageViewSetForProduct(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return super(ProductImageViewSetForProduct, self).get_queryset().filter(product=self.kwargs['id'])


class OrderStateViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = OrderState.objects.all()
    serializer_class = OrderStateSerializer


class PaymentDetailAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = PaymentDetail.objects.all()
    serializer_class = PaymentDetailSerializer

    def perform_create(self, serializer):
        payment_details = super(PaymentDetailAdmViewSet, self).perform_create(serializer)
        payment = Payment(is_paid=False, details=serializer.instance, token=create_hash())
        payment.save()
        return payment_details


class PaymentMethodAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
