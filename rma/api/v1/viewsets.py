import django_filters
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser, AllowAny

from permissions.views.viewsets import OwnsOrder
from rma.api.v1.serializers import ReturnMerchandiseAuthorizationConfigSerializer, \
    ReturnMerchandiseAuthorizationShipperSerializer, ReturnMerchandiseAuthorizationStateSerializer, \
    ReturnMerchandiseAuthorizationSerializer, ReturnMerchandiseAuthorizationItemSerializer, \
    ReturnMerchandiseAuthorizationOrderItemSerializer
from rma.models.main import ReturnMerchandiseAuthorizationConfig, ReturnMerchandiseAuthorizationShipper, \
    ReturnMerchandiseAuthorizationState, ReturnMerchandiseAuthorization, ReturnMerchandiseAuthorizationItem
from shop.api.v1.viewsets import OrderItemViewSet
from shop.models.orders import OrderItem


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

    def create(self, request, *args, **kwargs):
        request.data['contact'] = request.user.contact
        super(ReturnMerchandiseAuthorizationViewSet, self).create(request, *args, **kwargs)


class ReturnMerchandiseAuthorizationItemViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ReturnMerchandiseAuthorizationItem.objects.all()
    serializer_class = ReturnMerchandiseAuthorizationItemSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]



class ReturnMerchandiseAuthorizationOrderItemSetN(viewsets.ModelViewSet):
    permission_classes = [OwnsOrder]
    queryset = OrderItem.objects.all()
    serializer_class = ReturnMerchandiseAuthorizationOrderItemSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    lookup_field = 'order_detail__uuid'



class ReturnMerchandiseAuthorizationOrderItemSet(OrderItemViewSet):
    def get_queryset(self):
        queryset = super(ReturnMerchandiseAuthorizationOrderItemSet, self).get_queryset()
        queryset.filter()
        # todo filter for order and contact and eligible items.