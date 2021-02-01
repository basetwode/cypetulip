import django_filters
from rest_framework import routers, viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser

from accounting.api.viewsets.rest import AccountingOrderDetailPerYearViewSet
from management.api.serializers.rest import OrderSerializer, OrderDetailSerializer, OrderItemSerializer, \
    CompanySerializer, ProductSerializer, ProductCategorySerializer, ProductAttributeTypeSerializer, \
    ProductAttributeTypeInstanceSerializer, ProductSubItemSerializer, ProductImageSerializer, FileOrderItemSerializer, \
    SelectOrderItemSerializer, NumberOrderItemSerializer, CheckboxOrderItemSerializer, OrderStateSerializer, \
    PaymentDetailSerializer, PaymentMethodSerializer
from payment.models import PaymentDetail, PaymentMethod, Payment
from shop.api.viewsets.rest import AddressViewSet, GuestViewSet, ContactViewSet, DeliveryViewSet, OrderViewSet, \
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
        if 'contactId' in self.kwargs:
            contact = Contact.objects.get(id=self.kwargs['contactId'])
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


router = routers.DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'adm/contacts', ContactAdmViewSet)
router.register(r'adm/contacts/(?P<contactId>[0-9]*)/addresses', AddressAdmViewSet)
router.register(r'adm/orderstate', OrderStateViewSet)
router.register(r'adm/order', OrderAdmViewSet)
router.register(r'adm/orderdetails/(?P<order_hash>[a-zA-Z0-9\\s\-_ ]*)', OrderDetailAdmViewSet)
router.register(r'adm/orderdetails', OrderDetailAdmViewSet)
router.register(r'adm/orderitem', OrderItemAdmViewSet)
router.register(r'adm/fileorderitem', FileOrderItemAdmViewSet)
router.register(r'adm/checkboxorderitem', CheckboxOrderItemAdmViewSet)
router.register(r'adm/selectorderitem', SelectOrderItemAdmViewSet)
router.register(r'adm/numberorderitem', NumberOrderItemAdmViewSet)
router.register(r'adm/paymentdetail', PaymentDetailAdmViewSet)
router.register(r'adm/paymentmethod', PaymentMethodAdmViewSet)
router.register(r'products', ProductViewSet)
router.register(r'categories', ProductCategoryViewSet)
router.register(r'productattributetypes', ProductAttributeTypeViewSet)
router.register(r'productattributetypeinstances', ProductAttributeTypeInstanceViewSet)
router.register(r'productsubitem', ProductSubItemViewSet)
router.register(r'accounts', GuestViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'deliveries', DeliveryViewSet)
router.register(r'order', OrderViewSet)
router.register(r'voucher', ApplyVoucherViewSet)
router.register(r'orderitem', OrderItemViewSet)
router.register(r'fileorderitem', FileOrderItemViewSet)
router.register(r'selectorderitem', SelectOrderItemViewSet)
router.register(r'numberorderitem', NumberOrderItemViewSet)
router.register(r'checkboxorderitem', CheckboxOrderItemViewSet)
router.register(r'productimage', ProductImageViewSet)
router.register(r'product/(?P<productId>[0-9]*)/productimage', ProductImageViewSetForProduct)
router.register(r'accounting/orders/(?P<year>[0-9]{4})', AccountingOrderDetailPerYearViewSet)
