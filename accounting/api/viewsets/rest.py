from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser

from accounting.api.serializers.rest import AccountingOrderDetailSerializer
from shop.models import OrderDetail


class AccountingOrderDetailPerYearViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = OrderDetail.objects.values('date_bill__month') \
        .annotate(counted_orders=Count('date_bill__month'))
    serializer_class = AccountingOrderDetailSerializer
