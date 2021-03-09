from rest_framework import routers

from payment.api.v1.viewsets import PaymentDetailViewSet, PaymentMethodViewSet

router = routers.DefaultRouter()
router.register(r'paymentdetail', PaymentDetailViewSet)
router.register(r'paymentmethod', PaymentMethodViewSet)
