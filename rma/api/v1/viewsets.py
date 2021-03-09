import django_filters
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser

from rma.api.v1.serializers import ReturnMerchandiseAuthorizationConfigSerializer, \
    ReturnMerchandiseAuthorizationShipperSerializer, ReturnMerchandiseAuthorizationStateSerializer, \
    ReturnMerchandiseAuthorizationSerializer, ReturnMerchandiseAuthorizationItemSerializer
from rma.models.main import ReturnMerchandiseAuthorizationConfig, ReturnMerchandiseAuthorizationShipper, \
    ReturnMerchandiseAuthorizationState, ReturnMerchandiseAuthorization, ReturnMerchandiseAuthorizationItem


class ReturnMerchandiseAuthorizationConfigViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ReturnMerchandiseAuthorizationConfig.objects.all()
    serializer_class = ReturnMerchandiseAuthorizationConfigSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ReturnMerchandiseAuthorizationShipperViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ReturnMerchandiseAuthorizationShipper.objects.all()
    serializer_class = ReturnMerchandiseAuthorizationShipperSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ReturnMerchandiseAuthorizationStateViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ReturnMerchandiseAuthorizationState.objects.all()
    serializer_class = ReturnMerchandiseAuthorizationStateSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ReturnMerchandiseAuthorizationViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ReturnMerchandiseAuthorization.objects.all()
    serializer_class = ReturnMerchandiseAuthorizationSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ReturnMerchandiseAuthorizationItemViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ReturnMerchandiseAuthorizationItem.objects.all()
    serializer_class = ReturnMerchandiseAuthorizationItemSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
