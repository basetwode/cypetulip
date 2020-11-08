from rest_framework import viewsets, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.fields import Field, SerializerMethodField
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from shop.models import Address, Contact, Company, Order, OrderDetail, OrderItem, Product, ProductSubItem, FileSubItem, \
    SelectSubItem, CheckBoxSubItem, NumberSubItem, SelectItem, FileOrderItem, SelectOrderItem, NumberOrderItem, \
    CheckBoxOrderItem
from shop.utils import create_hash


class FileSubItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileSubItem
        fields = '__all__'


class SelectOptionSerializer(serializers.ModelSerializer):
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
        fields = ['stock', 'assigned_sub_products', 'product_picture']
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


    class Meta:
        model = ProductSubItem
        fields = '__all__'
        depth = 4


class OrderItemDeserializer(serializers.ModelSerializer):

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


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSubItemSerializer()
    randID = SerializerMethodField(source='get_rand_id')
    errors = SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product', 'price', 'price_wt', 'count', 'id', 'fileorderitem',
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

class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField('get_order_items')

    class Meta:
        model = OrderDetail
        fields = ['order_number', 'order', 'order_items', 'id']
        depth = 4

    def get_order_items(self, order):
        qs = OrderItem.objects.filter(order_detail=order, order_item__isnull=True)
        serializer = OrderItemSerializer(instance=qs, many=True)
        return serializer.data


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
                    address.contact = Contact.objects.get(user=self.request.user)
                    address.save()
                    return Response(address_serializer.data)
                else:
                    return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                address_serializer = AddressSerializer(data=request.data['address'])
                contact_serializer = ContactSerializer(data=request.data['contact'])
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
            contact = Contact.objects.get(user=user)
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
            return Contact.objects.filter(user=user)
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
                order_details.shipment_address = shipment_address
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
    queryset = OrderDetail.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order__order_hash'

    def get_queryset(self):
        """
        This view should return a list of all addresses
        for the currently authenticated user.
        """
        request = self.request
        if request.method == 'PUT':
            order_serializer = OrderSerializer(data=request.data)
            if order_serializer.is_valid():
                pass
            else :
                return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_authenticated:
            contact = Contact.objects.filter(user=request.user)
            if contact:
                company = contact[0].company
                return OrderDetail.objects.filter(state__isnull=True, order__company=company)
        else:
            return OrderDetail.objects.filter(is_send=False, order__session=request.session.session_key)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemDeserializer


class FileOrderItemViewSet(viewsets.ModelViewSet):
    queryset = FileOrderItem.objects.all()
    serializer_class = FileOrderItemSerializer


class SelectOrderItemViewSet(viewsets.ModelViewSet):
    queryset = SelectOrderItem.objects.all()
    serializer_class = SelectOrderItemSerializer

class NumberOrderItemViewSet(viewsets.ModelViewSet):
    queryset = NumberOrderItem.objects.all()
    serializer_class = NumberOrderItemSerializer

class CheckboxOrderItemViewSet(viewsets.ModelViewSet):
    queryset = CheckBoxOrderItem.objects.all()
    serializer_class = CheckboxOrderItemSerializer
