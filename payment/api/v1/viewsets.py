from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser

from payment.api.v1.serializers import PaymentDetailSerializer, PaymentMethodSerializer
from payment.models.main import PaymentDetail, PaymentMethod, Payment
from shop.utils import create_hash


class PaymentDetailViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = PaymentDetail.objects.all()
    serializer_class = PaymentDetailSerializer

    def perform_create(self, serializer):
        payment_details = super(PaymentDetailViewSet, self).perform_create(serializer)
        payment = Payment(is_paid=False, details=serializer.instance, token=create_hash())
        payment.save()
        return payment_details


class PaymentMethodViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
