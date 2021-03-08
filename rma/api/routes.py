from rest_framework import routers

from rma.api.v1.viewsets import ReturnMerchandiseAuthorizationConfigViewSet, \
    ReturnMerchandiseAuthorizationShipperViewSet, ReturnMerchandiseAuthorizationStateViewSet, \
    ReturnMerchandiseAuthorizationViewSet, ReturnMerchandiseAuthorizationItemViewSet

router = routers.DefaultRouter()
router.register(r'rma', ReturnMerchandiseAuthorizationViewSet)
router.register(r'rma/items', ReturnMerchandiseAuthorizationItemViewSet)
router.register(r'rma/config', ReturnMerchandiseAuthorizationConfigViewSet)
router.register(r'rma/shippers', ReturnMerchandiseAuthorizationShipperViewSet)
router.register(r'rma/states', ReturnMerchandiseAuthorizationStateViewSet)
