from rest_framework import routers, viewsets, serializers
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser

from payment.models import PaymentDetail, PaymentMethod
from shop.models import Product, ProductCategory, ProductAttributeType, ProductAttributeTypeInstance, ProductSubItem, \
    ProductImage, Company, Contact, Address, OrderDetail, OrderItem, CheckBoxOrderItem, NumberOrderItem, \
    SelectOrderItem, FileOrderItem, Order, OrderState
from shop.rest import AddressViewSet, GuestViewSet, ContactViewSet, DeliveryViewSet, OrderViewSet, OrderItemViewSet, \
    CheckboxOrderItemViewSet, NumberOrderItemViewSet, SelectOrderItemViewSet, FileOrderItemViewSet, ApplyVoucherViewSet, \
    ContactSerializer, AddressSerializer, OrderItemDeserializer


class ProductAttributeTypeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductAttributeType
        fields = '__all__'


class ProductAttributeTypeInstanceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductAttributeTypeInstance
        fields = '__all__'


class ProductCategorySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = '__all__'


class ProductSubItemSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductSubItem
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'

class OrderDetailSerializer(serializers.ModelSerializer):

    total = serializers.ReadOnlyField()
    total_wt = serializers.ReadOnlyField()

    class Meta:
        model = OrderDetail
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):

    total_wt = serializers.ReadOnlyField()
    period_of_performance_start = serializers.DateField(input_formats=['%Y-%m-%d',],required=False )
    period_of_performance_end = serializers.DateField(input_formats=['%Y-%m-%d',],required=False)

    class Meta:
        model = OrderItem
        fields = '__all__'


class FileOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileOrderItem
        fields = '__all__'


class SelectOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = SelectOrderItem
        fields = '__all__'


class NumberOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = NumberOrderItem
        fields = '__all__'


class CheckboxOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckBoxOrderItem
        fields = '__all__'

    def validate_is_checked(self, value):

        product = ProductSubItem.objects.get(id=self.initial_data['product'])
        if product.checkboxsubitem.is_required and not value:
            raise serializers.ValidationError(_('This field is required'))
        else:
            return value


class OrderStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderState
        fields = '__all__'


class PaymentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentDetail
        fields = '__all__'


class PaymentMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMethod
        fields = '__all__'

###############################################################


class OrderAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderDetailAdmViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer

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
        else :
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
router.register(r'fileorderitem',FileOrderItemViewSet)
router.register(r'selectorderitem',SelectOrderItemViewSet)
router.register(r'numberorderitem',NumberOrderItemViewSet)
router.register(r'checkboxorderitem',CheckboxOrderItemViewSet)
router.register(r'productimage', ProductImageViewSet)
router.register(r'product/(?P<productId>[0-9]*)/productimage', ProductImageViewSetForProduct)