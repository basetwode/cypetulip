from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from shop.models import Address, Contact, Company, OrderDetail, OrderItem, Product, ProductSubItem, FileSubItem, \
    SelectSubItem, CheckBoxSubItem, NumberSubItem, SelectItem, FileOrderItem, SelectOrderItem, NumberOrderItem, \
    CheckBoxOrderItem, Discount, ProductImage


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
    product_picture = serializers.SerializerMethodField('get_image')

    class Meta:
        model = Product
        fields = ['stock', 'assigned_sub_products', 'max_items_per_order', 'product_picture']
        depth = 4

    def get_image(self, object):
        return ProductImage.objects.filter(product=object).first().product_picture.url \
            if ProductImage.objects.filter(product=object).count() > 0 else None

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
    price = serializers.ReadOnlyField()
    total_wt = serializers.ReadOnlyField()
    allowable = serializers.HiddenField(default=True)
    period_of_performance_start = serializers.DateField(input_formats=['%Y-%m-%d', ], required=False)
    period_of_performance_end = serializers.DateField(input_formats=['%Y-%m-%d', ], required=False)

    class Meta:
        model = OrderItem
        fields = '__all__'


class FileOrderItemSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField()
    allowable = serializers.HiddenField(default=True)

    class Meta:
        model = FileOrderItem
        fields = '__all__'

    def validate_file(self, value):
        product = ProductSubItem.objects.get(id=self.initial_data['product'])
        extensions = product.filesubitem.extensions.split(",")

        if len(extensions) <= 1:
            return value
        elif value.name.split(".")[-1] in extensions:
            return value
        else:
            raise serializers.ValidationError(_("Unsupported filetype, supported files are " + product.
                                                filesubitem.extensions))


class SelectOrderItemSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField()
    allowable = serializers.HiddenField(default=True)

    class Meta:
        model = SelectOrderItem
        fields = '__all__'


class NumberOrderItemSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField()
    allowable = serializers.HiddenField(default=True)

    class Meta:
        model = NumberOrderItem
        fields = '__all__'


class CheckboxOrderItemSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField()
    allowable = serializers.HiddenField(default=True)

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
    price = serializers.ReadOnlyField()
    product = ProductSubItemSerializer()
    randID = SerializerMethodField(source='get_rand_id')
    errors = SerializerMethodField()
    valid = SerializerMethodField()
    total_wt = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['product', 'price', 'price_wt', 'count', 'id', 'fileorderitem', 'valid', 'applied_discount',
                  'allowable',
                  'price_discounted', 'price_discounted_wt', 'total_wt', 'period_of_performance_start',
                  'period_of_performance_end',
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
        if not voucher.exists():
            raise serializers.ValidationError(_('Voucher code invalid'))
        voucher = voucher.first()
        if voucher.is_invalid():
            raise serializers.ValidationError(_('Voucher code invalid'))

        voucher_applied = order_detail.apply_voucher(voucher)
        if not voucher_applied:
            raise serializers.ValidationError(_('Voucher code not eligible'))
