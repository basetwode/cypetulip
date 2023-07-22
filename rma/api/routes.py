from rest_framework import routers

from rma.api.v1.viewsets import ReturnMerchandiseAuthorizationConfigViewSet, \
    ReturnMerchandiseAuthorizationShipperViewSet, ReturnMerchandiseAuthorizationStateViewSet, \
    ReturnMerchandiseAuthorizationViewSet, \
    ReturnMerchandiseAuthorizationOrderItemSetN, ReturnMerchandiseAuthorizationOrderItemSet

router = routers.DefaultRouter()
router.register(r'', ReturnMerchandiseAuthorizationViewSet)
router.register(r'items/', ReturnMerchandiseAuthorizationOrderItemSetN)

router.register(r'config', ReturnMerchandiseAuthorizationConfigViewSet)
router.register(r'shippers', ReturnMerchandiseAuthorizationShipperViewSet)
router.register(r'states', ReturnMerchandiseAuthorizationStateViewSet)
