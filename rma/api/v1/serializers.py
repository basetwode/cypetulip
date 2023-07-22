from rest_framework import serializers

from rma.models.main import ReturnMerchandiseAuthorizationConfig, ReturnMerchandiseAuthorizationShipper, \
    ReturnMerchandiseAuthorizationState, ReturnMerchandiseAuthorization, ReturnMerchandiseAuthorizationItem
from shop.models.orders import OrderItem


class ReturnMerchandiseAuthorizationConfigSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ReturnMerchandiseAuthorizationConfig
        fields = '__all__'


class ReturnMerchandiseAuthorizationShipperSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ReturnMerchandiseAuthorizationShipper
        fields = '__all__'


class ReturnMerchandiseAuthorizationStateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ReturnMerchandiseAuthorizationState
        fields = '__all__'


class ReturnMerchandiseAuthorizationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    contact = serializers.ReadOnlyField()

    class Meta:
        model = ReturnMerchandiseAuthorization
        fields = '__all__'


class ReturnMerchandiseAuthorizationItemSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ReturnMerchandiseAuthorizationItem
        fields = '__all__'


class ReturnMerchandiseAuthorizationOrderItemSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'count', 'price_wt', 'is_conveyed', 'get_shipment']
        lookup_field = 'order_detail__uuid'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
