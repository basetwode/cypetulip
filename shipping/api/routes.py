from rest_framework import routers

from shipping.api.v1.viewsets import ContinentViewSet, CountryViewSet, ShipperViewSet, PackageViewSet, \
    OnlineShipmentViewSet, PackageShipmentViewSet

router = routers.DefaultRouter()
router.register(r'continents', ContinentViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'shippers', ShipperViewSet)
router.register(r'packages', PackageViewSet)
router.register(r'shipments/packages', PackageShipmentViewSet)
router.register(r'shipments/online', OnlineShipmentViewSet)
