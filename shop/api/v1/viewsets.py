import secrets

from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from management.api.v1.serializers import FullOrderItemSerializer, FullFileOrderItemSerializer, \
    FullCheckboxOrderItemSerializer, FullNumberOrderItemSerializer, FullSelectOrderItemSerializer
from shop.api.v1.serializers import AddressSerializer, BasicContactSerializer, OrderShipmentSerializer, \
    VoucherSerializer, BasicOrderItemSerializer, BasicFileOrderItemSerializer, \
    BasicSelectOrderItemSerializer, \
    BasicNumberOrderItemSerializer, BasicCheckboxOrderItemSerializer, OrderDetailSerializer, FullOrderDetailSerializer
from shop.models import Address, Contact, Company, Order, OrderDetail, OrderItem, FileOrderItem, SelectOrderItem, \
    NumberOrderItem, \
    CheckBoxOrderItem, Discount
from shop.utils import create_hash


class GuestViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    queryset = Company.objects.all()

    def create(self, request):
        """
        Create a new account based on contact, company and address.
        """
        if request.method == 'POST':
            if self.request.user.is_authenticated:
                address_serializer = AddressSerializer(data=request.data['address'])
                if address_serializer.is_valid():
                    address = address_serializer.save()
                    address.contact = Contact.objects.get(user_ptr=self.request.user)
                    address.save()
                    return Response(address_serializer.data)
                else:
                    return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                address_serializer = AddressSerializer(data=request.data['address'])
                contact_serializer = BasicContactSerializer(data={**request.data['contact'], **{
                    'password': secrets.token_hex(32),
                    'username': request.data['contact']['email'] + "_" + secrets.token_hex(6),
                    'session': request.session.session_key,
                    'email': request.data['contact']['email'],
                }})
                if address_serializer.is_valid():
                    address = address_serializer.save()
                if contact_serializer.is_valid():
                    contact = contact_serializer.save()
                    address.contact = contact
                    address.save()
                    return Response(address_serializer.data)
                else:
                    errors = {**address_serializer.errors, **contact_serializer.errors}
                    errors.pop("company", None)
                    return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return FullOrderDetailSerializer
        return OrderDetailSerializer

    def get_queryset(self):
        queryset = OrderDetail.objects.all()
        request = self.request
        result = None
        if request.user.is_authenticated and request.user.is_staff:
            order_hash = self.request.query_params.get('orderHash', None)
            order_year = self.request.query_params.get('orderYear', None)
            if order_hash is not None:
                return queryset.filter(order__order_hash=order_hash)
            if order_year is not None:
                return queryset.filter(date_bill__year=order_year)
        if request.user.is_authenticated:
            contact = Contact.objects.filter(user_ptr=request.user)
            if contact:
                company = contact[0].company
                result = OrderDetail.objects.filter(state__isnull=True, order__company=company)
        else:
            result = OrderDetail.objects.filter(state__isnull=True, order__session=request.session.session_key)
        if result:
            return result
        else:
            order, order_detail = Order.create_new_order(request)
            return OrderDetail.objects.filter(id=order_detail.id)


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        """
        This view should return a list of all addresses
        for the currently authenticated user.
        """
        if self.request.user.is_staff:
            if 'id' in self.kwargs:
                contact = Contact.objects.get(id=self.kwargs['id'])
                return Address.objects.filter(contact__in=contact.company.contact_set.all())
            else:
                return super(AddressViewSet, self).get_queryset()
        if self.request.user.is_authenticated:
            user = self.request.user
            contact = Contact.objects.get(user_ptr=user)
            return Address.objects.filter(contact__in=contact.company.contact_set.all())
        else:
            raise NotFound()


class ContactViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Contact.objects.all()
    serializer_class = BasicContactSerializer

    def get_queryset(self):
        """
        This view should return a contact for the currently authenticated user
        """
        if self.request.user.is_staff:
            return super(ContactViewSet, self).get_queryset()
        if self.request.user.is_authenticated:
            user = self.request.user
            return Contact.objects.filter(user_ptr=user)
        else:
            raise NotFound()


class DeliveryViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    queryset = Order.objects.all()
    serializer_class = OrderShipmentSerializer

    def create(self, request):
        order_serializer = OrderShipmentSerializer(data=request.data)
        if order_serializer.is_valid():
            order = request.data['order']
            _order = Order.objects.filter(order_hash=order, is_send=False)
            order_details = OrderDetail.objects.get(order_number=order)
            if _order.count() > 0:
                token = create_hash()
                shipment_address = Address.objects.get(id=request.data['shipment'])
                billing_address = Address.objects.get(id=request.data['billing'])
                order_details.shipment_address = shipment_address
                order_details.billing_address = billing_address
                order_details.save()
                ord = _order[0]
                ord.token = token
                ord.save()
                return Response(order_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = OrderItem.objects.all()
    serializer_class = BasicOrderItemSerializer

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return FullOrderItemSerializer
        return BasicOrderItemSerializer

    def get_queryset(self):
        queryset = super(OrderItemViewSet, self).get_queryset()
        if self.request.user.is_staff:
            return queryset
        if self.request.user.is_authenticated:
            queryset = queryset.filter(order__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset = queryset.filter(order__session=self.request.session.session_key)
        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        stock_sufficient, curr_stock = instance.product.product.is_stock_sufficient(instance.order)
        new_items = request.data.get('count') - instance.count

        if request.data.get('count') > instance.product.product.max_items_per_order:
            return Response({'error': _('We\'re sorry, you can only add up to %(count) items to your order') % {
                'article': instance.product.product.max_items_per_order},
                             'count': instance.count
                             }, status=status.HTTP_400_BAD_REQUEST)

        if new_items <= curr_stock or instance.product.product.stock < 0:
            instance.count = request.data.get("count")
            instance.save()
            return Response({}, status=status.HTTP_200_OK)

        return Response({'error': _('We\'re sorry, we can not add %(article)s to your shopping '
                                    'cart because our stocks are insufficient') % {
                                      'article': instance.product.product.name},
                         'count': instance.count
                         }, status=status.HTTP_400_BAD_REQUEST)


class FileOrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = FileOrderItem.objects.all()
    serializer_class = BasicFileOrderItemSerializer

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return FullFileOrderItemSerializer
        return BasicFileOrderItemSerializer

    def get_queryset(self):
        queryset = super(FileOrderItemViewSet, self).get_queryset()
        if self.request.user.is_staff:
            return queryset
        if self.request.user.is_authenticated:
            queryset.filter(order__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order__session=self.request.session.session_key)
        return queryset


class SelectOrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = SelectOrderItem.objects.all()
    serializer_class = BasicSelectOrderItemSerializer

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return FullSelectOrderItemSerializer
        return BasicSelectOrderItemSerializer

    def get_queryset(self):
        queryset = super(SelectOrderItemViewSet, self).get_queryset()
        if self.request.user.is_staff:
            return queryset
        if self.request.user.is_authenticated:
            queryset.filter(order__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order__session=self.request.session.session_key)
        return queryset


class NumberOrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = NumberOrderItem.objects.all()
    serializer_class = BasicNumberOrderItemSerializer

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return FullNumberOrderItemSerializer
        return BasicNumberOrderItemSerializer

    def get_queryset(self):
        queryset = super(NumberOrderItemViewSet, self).get_queryset()
        if self.request.user.is_staff:
            return queryset
        if self.request.user.is_authenticated:
            queryset.filter(order__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order__session=self.request.session.session_key)
        return queryset


class CheckboxOrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = CheckBoxOrderItem.objects.all()
    serializer_class = BasicCheckboxOrderItemSerializer

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return FullCheckboxOrderItemSerializer
        return BasicCheckboxOrderItemSerializer

    def get_queryset(self):
        queryset = super(CheckboxOrderItemViewSet, self).get_queryset()
        if self.request.user.is_staff:
            return queryset
        if self.request.user.is_authenticated:
            queryset.filter(order__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order__session=self.request.session.session_key)
        return queryset


class ApplyVoucherViewSet(viewsets.ViewSet):
    queryset = Discount.objects.all()
    permission_classes = [AllowAny]
    serializer_class = VoucherSerializer

    def create(self, request):
        voucher_serializer = VoucherSerializer(data=request.data)

        if voucher_serializer.is_valid():
            return Response(voucher_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(voucher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
