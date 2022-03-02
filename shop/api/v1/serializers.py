from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from shop.models.accounts import Address, Contact, WorkingTime, Company
from shop.models.orders import OrderItem, CheckBoxOrderItem, NumberOrderItem, \
    SelectOrderItem, FileOrderItem, OrderState, OrderDetail, Discount, OrderItemState, PercentageDiscount, \
    FixedAmountDiscount
from shop.models.products import Product, ProductCategory, ProductAttributeType, ProductAttributeTypeInstance, \
    ProductSubItem, \
    ProductImage, FileSubItem, SelectItem, SelectSubItem, CheckBoxSubItem, NumberSubItem, FileExtensionItem, \
    IndividualOffer


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


class BasicProductSerializer(serializers.ModelSerializer):
    product_picture = serializers.SerializerMethodField('get_image')

    class Meta:
        model = Product
        fields = ['stock', 'assigned_sub_products', 'max_items_per_order', 'product_picture']
        depth = 4

    def get_image(self, object):
        return ProductImage.objects.filter(product=object).first().product_picture.url \
            if ProductImage.objects.filter(product=object).count() > 0 else None

    def get_fields(self):
        fields = super(BasicProductSerializer, self).get_fields()
        fields['assigned_sub_products'] = ProductSubItemSerializer(many=True)
        return fields


class FullProductSerializer(BasicProductSerializer):
    is_public = serializers.BooleanField(write_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductSubItemSerializer(serializers.ModelSerializer):
    product = BasicProductSerializer()
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


class BasicOrderItemSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField()
    total_wt = serializers.ReadOnlyField()
    allowable = serializers.HiddenField(default=True)
    period_of_performance_start = serializers.DateField(input_formats=['%Y-%m-%d', ], required=False)
    period_of_performance_end = serializers.DateField(input_formats=['%Y-%m-%d', ], required=False)

    class Meta:
        model = OrderItem
        fields = '__all__'


class BasicFileOrderItemSerializer(serializers.ModelSerializer):
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


class BasicSelectOrderItemSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField()
    allowable = serializers.HiddenField(default=True)

    class Meta:
        model = SelectOrderItem
        fields = '__all__'


class BasicNumberOrderItemSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField()
    allowable = serializers.HiddenField(default=True)

    class Meta:
        model = NumberOrderItem
        fields = '__all__'


class BasicCheckboxOrderItemSerializer(serializers.ModelSerializer):
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


class OrderDetailSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()
    total_wt = serializers.ReadOnlyField()
    tax = serializers.ReadOnlyField()
    order_items = serializers.SerializerMethodField('get_order_items')
    voucher = SerializerMethodField()

    class Meta:
        model = OrderDetail
        fields = ['uuid',
                  'order_items', 'tax',
                  'id', 'voucher', 'total_wt', 'total', 'date_bill']
        depth = 4

    def get_order_items(self, order):
        qs = OrderItem.objects.filter(order_detail=order, order_item__isnull=True)
        serializer = OrderItemSerializer(instance=qs, many=True)
        return serializer.data

    def get_voucher(self, object):
        return object.discount.voucher_id if object.discount else ""


class FullOrderDetailSerializer(OrderDetailSerializer):
    id = serializers.ReadOnlyField()
    unique_nr = serializers.ReadOnlyField()

    class Meta:
        model = OrderDetail
        fields = '__all__'

    def create(self, request):
        contact = request.get('contact', None)
        request['company'] = contact.company
        return OrderDetail.objects.create(**request)


class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField()
    product = ProductSubItemSerializer()
    randID = SerializerMethodField(source='get_rand_id')
    errors = SerializerMethodField()
    valid = SerializerMethodField()
    total_wt = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['product', 'price_discounted', 'price_wt', 'count', 'id', 'fileorderitem', 'valid', 'applied_discount',
                  'allowable', 'price', 'price_admin',
                  'price_discounted', 'price_discounted_wt', 'total_wt', 'period_of_performance_start',
                  'period_of_performance_end', 'is_conveyed',
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


class CompanySerializer(serializers.ModelSerializer):
    def create(self, request):
        return Company.objects.create(**request)

    class Meta:
        model = Company
        fields = '__all__'


class BasicContactSerializer(serializers.ModelSerializer):
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

    get_name = serializers.ReadOnlyField()

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
    uuid = serializers.CharField(max_length=40, required=False)

    def validate_voucher(self, value):

        order_detail = OrderDetail.objects.get(uuid=self.initial_data['uuid'])
        voucher = Discount.objects.filter(voucher_id=value)
        if not voucher.exists():
            raise serializers.ValidationError(_('Voucher code invalid'))
        voucher = voucher.first()
        if voucher.is_invalid():
            raise serializers.ValidationError(_('Voucher code invalid'))

        voucher_applied = order_detail.apply_voucher(voucher)
        if not voucher_applied:
            raise serializers.ValidationError(_('Voucher code not eligible'))


class ProductAttributeTypeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductAttributeType
        fields = '__all__'


class ProductAttributeTypeInstanceSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductAttributeTypeInstance
        fields = '__all__'


class ProductCategorySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class FullOrderItemSerializer(serializers.ModelSerializer):
    total_wt = serializers.ReadOnlyField()
    period_of_performance_start = serializers.DateField(input_formats=['%Y-%m-%d', ], required=False)
    period_of_performance_end = serializers.DateField(input_formats=['%Y-%m-%d', ], required=False)

    class Meta:
        model = OrderItem
        fields = '__all__'


class FullFileOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileOrderItem
        fields = '__all__'


class FullSelectOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectOrderItem
        fields = '__all__'


class FullNumberOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberOrderItem
        fields = '__all__'


class FullCheckboxOrderItemSerializer(serializers.ModelSerializer):
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


class FileExtensionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileExtensionItem
        fields = '__all__'


class SelectItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectItem
        fields = '__all__'


class OrderItemStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemState
        fields = '__all__'


class IndividualOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndividualOffer
        fields = '__all__'


class PercentageDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PercentageDiscount
        fields = '__all__'


class FixedAmountDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedAmountDiscount
        fields = '__all__'


class WorkingTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingTime
        fields = '__all__'
