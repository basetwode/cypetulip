from rest_framework import serializers

from shop.models import OrderDetail


class AccountingOrderDetailSerializer(serializers.ModelSerializer):
    counted_orders = serializers.JSONField()
    date_bill__month = serializers.JSONField()

    class Meta:
        model = OrderDetail
        fields = ['counted_orders', 'date_bill__month']
