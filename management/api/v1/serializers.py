from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from payment.models.main import PaymentDetail, PaymentMethod
from shop.models.orders import OrderState, Order, OrderItem, FileOrderItem, SelectOrderItem, CheckBoxOrderItem, \
    NumberOrderItem
from shop.models.products import ProductCategory, ProductSubItem, ProductAttributeType, ProductAttributeTypeInstance, \
    Product, ProductImage
from shop.models.accounts import Company


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
    def create(self, request):
        return Company.objects.create(**request)

    class Meta:
        model = Company
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
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


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetail
        fields = '__all__'


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'
