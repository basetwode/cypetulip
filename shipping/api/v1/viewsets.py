import django_filters
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser

from shipping.api.v1.serializers import ContinentSerializer, CountrySerializer, ShipperSerializer, PackageSerializer, \
    PackageShipmentSerializer, OnlineShipmentSerializer
from shipping.models.main import Continent, Country, Shipper, Package, PackageShipment, OnlineShipment


class ContinentViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Continent.objects.all()
    serializer_class = ContinentSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class CountryViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ShipperViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Shipper.objects.all()
    serializer_class = ShipperSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class PackageViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class PackageShipmentViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = PackageShipment.objects.all()
    serializer_class = PackageShipmentSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class OnlineShipmentViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = OnlineShipment.objects.all()
    serializer_class = OnlineShipmentSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
