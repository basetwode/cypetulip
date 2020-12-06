import secrets

from django.contrib import messages
from rest_framework import viewsets, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.fields import Field, SerializerMethodField
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.utils.translation import ugettext_lazy as _

from shop.models import Address, Contact, Company, Order, OrderDetail, OrderItem, Product, ProductSubItem, FileSubItem, \
    SelectSubItem, CheckBoxSubItem, NumberSubItem, SelectItem, FileOrderItem, SelectOrderItem, NumberOrderItem, \
    CheckBoxOrderItem, Discount
from shop.utils import create_hash


class FileSubItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileSubItem
        fields = '__all__'


class SelectOptionSerializer(serializers.ModelSerializer):
    price_wt = serializers.FloatField(required=False)

    class Meta:
        model = SelectItem
        fields = '__all__'


class SelectSubItemSerializer(serializers.ModelSerializer):
    options = SelectOptionSerializer(source="selectitem_set", many=True)

    class Meta:
        model = SelectSubItem
        fields = '__all__'


class CheckBoxSubItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckBoxSubItem
        fields = '__all__'


class NumberSubItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = NumberSubItem
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['stock', 'assigned_sub_products', 'product_picture', 'max_items_per_order']
        depth = 4

    def get_fields(self):
        fields = super(ProductSerializer, self).get_fields()
        fields['assigned_sub_products'] = ProductSubItemSerializer(many=True)
        return fields


class ProductSubItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    numbersubitem = NumberSubItemSerializer()
    checkboxsubitem = CheckBoxSubItemSerializer()
    filesubitem = FileSubItemSerializer()
    selectsubitem = SelectSubItemSerializer()
    bprice_wt = serializers.FloatField(required=False)
    valid = SerializerMethodField()


    class Meta:
        model = ProductSubItem
        fields = '__all__'
        depth = 4

    def get_valid(self, object):
        return True


class OrderItemDeserializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = '__all__'


class FileOrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileOrderItem
        fields = '__all__'

    def validate_file(self, value):
        product = ProductSubItem.objects.get(id=self.initial_data['product'])
        extensions = product.filesubitem.extensions.split(",")

        if len(extensions)<=1:
            return value
        elif value.name.split(".")[-1] in extensions:
            return value
        else:
            raise serializers.ValidationError(_("Unsupported filetype, supported files are "+ product.
                                                filesubitem.extensions))


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


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSubItemSerializer()
    randID = SerializerMethodField(source='get_rand_id')
    errors = SerializerMethodField()
    valid = SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product', 'price', 'price_wt', 'count', 'id', 'fileorderitem', 'valid', 'applied_discount',
                  'price_discounted', 'price_discounted_wt',
                  'numberorderitem', 'selectorderitem', 'checkboxorderitem', 'randID', 'errors']
        depth = 4

    def get_fields(self):
        fields = super(OrderItemSerializer, self).get_fields()
        fields['order_items'] = OrderItemSerializer(source="orderitem_set", many=True)
        return fields

    def get_randID(self, object):
        import uuid
        return uuid.uuid4()

    def get_errors(self, object):
        return []

    def get_valid(self, object):
        return True


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField('get_order_items')
    voucher = SerializerMethodField()

    class Meta:
        model = OrderDetail
        fields = ['order_number', 'order', 'order_items', 'id', 'voucher']
        depth = 4

    def get_order_items(self, order):
        qs = OrderItem.objects.filter(order_detail=order, order_item__isnull=True)
        serializer = OrderItemSerializer(instance=qs, many=True)
        return serializer.data

    def get_voucher(self, object):
        return object.discount.voucher_id if object.discount else ""


class CompanySerializer(serializers.ModelSerializer):
    def create(self, request):
        return Company.objects.create(**request)

    class Meta:
        model = Company
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    def create(self, request):
        company = request.pop('company', None)
        if company:
            company = Company.objects.create(**company)
            request['company'] = company
        return Contact.objects.create(**request)

    class Meta:
        model = Contact
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):

    def create(self, request):
        return Address.objects.create(**request)

    class Meta:
        model = Address
        fields = '__all__'


class OrderShipmentSerializer(serializers.Serializer):
    order = serializers.CharField(max_length=200, required=False)
    shipment = serializers.CharField()
    billing = serializers.CharField()


class VoucherSerializer(serializers.Serializer):
    voucher = serializers.CharField(max_length=20, required=False)
    order_hash = serializers.CharField(max_length=40, required=False)

    def validate_voucher(self, value):

        order_detail = OrderDetail.objects.get(order__order_hash=self.initial_data['order_hash'])
        voucher = Discount.objects.filter(voucher_id=value)
        if not voucher.exists() :
            raise serializers.ValidationError(_('Voucher code invalid'))
        voucher = voucher.first()
        if voucher.is_invalid():
            raise serializers.ValidationError(_('Voucher code invalid'))

        voucher_applied = order_detail.apply_voucher(voucher)
        if not voucher_applied:
            raise serializers.ValidationError(_('Voucher code not eligible'))


###############################################################




class GuestViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    queryset = Company.objects.all()

    def create(self, request):
        """
        Create a new account based on contact, company and address.
        """
        if request.method == 'POST':
            if self.request.user.is_authenticated:
                address_serializer = AddressSerializer(data=request.data['address'])
                if address_serializer.is_valid():
                    address = address_serializer.save()
                    address.contact = Contact.objects.get(user_ptr=self.request.user)
                    address.save()
                    return Response(address_serializer.data)
                else:
                    return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                address_serializer = AddressSerializer(data=request.data['address'])
                contact_serializer = ContactSerializer(data={**request.data['contact'],**{
                    'password': secrets.token_hex(32),
                    'username': request.data['contact']['email']+"_"+secrets.token_hex(6),
                    'email': request.data['contact']['email'],
                }})
                if address_serializer.is_valid():
                    address = address_serializer.save()
                if contact_serializer.is_valid():
                    contact = contact_serializer.save()
                    address.contact = contact
                    address.save()
                    return Response(address_serializer.data)
                else:
                    errors = {**address_serializer.errors, **contact_serializer.errors}
                    errors.pop("company", None)
                    return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        """
        This view should return a list of all addresses
        for the currently authenticated user.
        """
        if self.request.user.is_authenticated:
            user = self.request.user
            contact = Contact.objects.get(user_ptr=user)
            return Address.objects.filter(contact=contact)
        else:
            raise NotFound()


class ContactViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_queryset(self):
        """
        This view should return a contact for the authenticated user
        for the currently authenticated user.
        """
        if self.request.user.is_authenticated:
            user = self.request.user
            return Contact.objects.filter(user_ptr=user)
        else:
            raise NotFound()


class DeliveryViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    queryset = Order.objects.all()

    def create(self, request):
        order_serializer = OrderShipmentSerializer(data=request.data)
        if order_serializer.is_valid():
            order = request.data['order']
            _order = Order.objects.filter(order_hash=order, is_send=False)
            order_details = OrderDetail.objects.get(order_number=order)
            if _order.count() > 0:
                token = create_hash()
                shipment_address = Address.objects.get(id=request.data['shipment'])
                billing_address = Address.objects.get(id=request.data['billing'])
                order_details.shipment_address = shipment_address
                order_details.billing_address = billing_address
                order_details.save()
                ord = _order[0]
                ord.token = token
                ord.save()
                return Response(order_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = OrderDetail.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order__order_hash'

    def get_queryset(self):
        """
        This view should return a list of all addresses
        for the currently authenticated user.
        """
        request = self.request
        result = None
        if request.user.is_authenticated:
            contact = Contact.objects.filter(user_ptr=request.user)
            if contact:
                company = contact[0].company
                result = OrderDetail.objects.filter(state__isnull=True, order__company=company)
        else:
            result = OrderDetail.objects.filter(state__isnull=True, order__session=request.session.session_key)
        if result:
            return result
        else:
            order, order_detail = Order.create_new_order(request)
            return OrderDetail.objects.filter(id=order_detail.id)


class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemDeserializer

    def get_queryset(self):
        queryset = super(OrderItemViewSet, self).get_queryset()
        if self.request.user.is_authenticated:
            queryset.filter(order__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order__session=self.request.session.session_key)
        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        stock_sufficient, curr_stock = instance.product.product.is_stock_sufficient(instance.order)
        new_items = request.data.get('count') - instance.count

        if request.data.get('count') > instance.product.product.max_items_per_order:
            return Response({'error': _('We\'re sorry, you can only add up to %(count) items to your order') % {
                                          'article': instance.product.product.max_items_per_order},
                             'count': instance.count
                             }, status=status.HTTP_400_BAD_REQUEST)

        if new_items <= curr_stock or instance.product.product.stock < 0:
            instance.count = request.data.get("count")
            instance.save()
            return Response({}, status=status.HTTP_200_OK)

        return Response({'error': _('We\'re sorry, we can not add %(article)s to your shopping '
                                    'cart because our stocks are insufficient') % {
                                      'article': instance.product.product.name},
                         'count': instance.count
                         }, status=status.HTTP_400_BAD_REQUEST)



class FileOrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = FileOrderItem.objects.all()
    serializer_class = FileOrderItemSerializer

    def get_queryset(self):
        queryset = super(FileOrderItemViewSet, self).get_queryset()
        if self.request.user.is_authenticated:
            queryset.filter(order__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order__session=self.request.session.session_key)
        return queryset


class SelectOrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = SelectOrderItem.objects.all()
    serializer_class = SelectOrderItemSerializer

    def get_queryset(self):
        queryset = super(SelectOrderItemViewSet, self).get_queryset()
        if self.request.user.is_authenticated:
            queryset.filter(order__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order__session=self.request.session.session_key)
        return queryset


class NumberOrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = NumberOrderItem.objects.all()
    serializer_class = NumberOrderItemSerializer

    def get_queryset(self):
        queryset = super(NumberOrderItemViewSet, self).get_queryset()
        if self.request.user.is_authenticated:
            queryset.filter(order__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order__session=self.request.session.session_key)
        return queryset


class CheckboxOrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = CheckBoxOrderItem.objects.all()
    serializer_class = CheckboxOrderItemSerializer

    def get_queryset(self):
        queryset = super(CheckboxOrderItemViewSet, self).get_queryset()
        if self.request.user.is_authenticated:
            queryset.filter(order__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order__session=self.request.session.session_key)
        return queryset


class ApplyVoucherViewSet(viewsets.ViewSet):
    queryset = Discount.objects.all()
    permission_classes = [AllowAny]
    serializer_class = VoucherSerializer

    def create(self, request):
        voucher_serializer = VoucherSerializer(data=request.data)

        if voucher_serializer.is_valid():
            return Response(voucher_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(voucher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
