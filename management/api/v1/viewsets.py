import django_filters
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser

from management.api.v1.serializers import OrderSerializer, OrderDetailSerializer, OrderItemSerializer, \
    CompanySerializer, ProductSerializer, ProductCategorySerializer, ProductAttributeTypeSerializer, \
    ProductAttributeTypeInstanceSerializer, ProductSubItemSerializer, ProductImageSerializer, FileOrderItemSerializer, \
    SelectOrderItemSerializer, NumberOrderItemSerializer, CheckboxOrderItemSerializer, OrderStateSerializer, \
    PaymentDetailSerializer, PaymentMethodSerializer
from payment.models import PaymentDetail, PaymentMethod, Payment
from shop.api.v1.viewsets import AddressViewSet, GuestViewSet, ContactViewSet, DeliveryViewSet, OrderViewSet, \
    OrderItemViewSet, \
    CheckboxOrderItemViewSet, NumberOrderItemViewSet, SelectOrderItemViewSet, FileOrderItemViewSet, ApplyVoucherViewSet, \
    ContactSerializer, AddressSerializer
from shop.models import Product, ProductCategory, ProductAttributeType, ProductAttributeTypeInstance, ProductSubItem, \
    ProductImage, Company, Contact, Address, OrderDetail, OrderItem, CheckBoxOrderItem, NumberOrderItem, \
    SelectOrderItem, FileOrderItem, Order, OrderState
from shop.utils import create_hash


class OrderAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderDetailAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_queryset(self):
        if 'order_hash' in self.kwargs:
            return OrderDetail.objects.filter(order__order_hash=self.kwargs['order_hash'])
        else:
            return super(OrderDetailAdmViewSet, self).get_queryset()


class OrderItemAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class ContactAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class AddressAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        if 'id' in self.kwargs:
            contact = Contact.objects.get(id=self.kwargs['id'])
            return Address.objects.filter(contact__in=contact.company.contact_set.all())
        else:
            return super(AddressAdmViewSet, self).get_queryset()


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
        return super(ProductImageViewSetForProduct, self).get_queryset().filter(product=self.kwargs['productId'])


class FileOrderItemAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = FileOrderItem.objects.all()
    serializer_class = FileOrderItemSerializer


class SelectOrderItemAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = SelectOrderItem.objects.all()
    serializer_class = SelectOrderItemSerializer


class NumberOrderItemAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = NumberOrderItem.objects.all()
    serializer_class = NumberOrderItemSerializer


class CheckboxOrderItemAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = CheckBoxOrderItem.objects.all()
    serializer_class = CheckboxOrderItemSerializer


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
