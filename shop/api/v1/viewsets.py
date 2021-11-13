import secrets

from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser
from rest_framework.response import Response

from shop.api.v1.serializers import AddressSerializer, BasicContactSerializer, OrderShipmentSerializer, \
    VoucherSerializer, BasicOrderItemSerializer, BasicFileOrderItemSerializer, \
    BasicSelectOrderItemSerializer, \
    BasicNumberOrderItemSerializer, BasicCheckboxOrderItemSerializer, OrderDetailSerializer, FullOrderDetailSerializer, \
    FullOrderItemSerializer, FullFileOrderItemSerializer, \
    FullCheckboxOrderItemSerializer, FullNumberOrderItemSerializer, FullSelectOrderItemSerializer, \
    CompanySerializer, BasicProductSerializer, \
    ProductCategorySerializer, ProductAttributeTypeSerializer, \
    ProductAttributeTypeInstanceSerializer, ProductSubItemSerializer, ProductImageSerializer, OrderStateSerializer, \
    FileExtensionItemSerializer, \
    SelectItemSerializer, OrderItemStateSerializer, IndividualOfferSerializer, FixedAmountDiscountSerializer, \
    PercentageDiscountSerializer, WorkingTimeSerializer, FullProductSerializer
from shop.models.accounts import Address, Contact, WorkingTime, Company
from shop.models.orders import OrderItem, CheckBoxOrderItem, NumberOrderItem, \
    SelectOrderItem, FileOrderItem, OrderState, OrderDetail, Discount, OrderItemState, PercentageDiscount, \
    FixedAmountDiscount
from shop.models.products import Product, ProductCategory, ProductAttributeType, ProductAttributeTypeInstance, \
    ProductSubItem, \
    ProductImage, SelectItem, FileExtensionItem, \
    IndividualOffer


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
        queryset = super(OrderDetailViewSet, self).get_queryset()
        request = self.request
        uuid = self.request.query_params.get('uuid', None)
        if request.user.is_authenticated and request.user.is_staff:
            order_year = self.request.query_params.get('orderYear', None)
            if uuid is not None:
                return queryset.filter(uuid=uuid)
            if order_year is not None:
                queryset = queryset.filter(date_bill__year=order_year)
            return queryset
        elif request.user.is_authenticated:
            contact = Contact.objects.get(user_ptr=request.user)
            queryset = queryset.filter(company=contact.company)
        return queryset


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return FullOrderDetailSerializer
        return OrderDetailSerializer

    # TODO: this needs to be refactored
    def get_queryset(self):
        queryset = OrderDetail.objects.all()
        request = self.request
        result = None
        uuid = self.request.query_params.get('uuid', None)
        if request.user.is_authenticated and request.user.is_staff:
            order_year = self.request.query_params.get('orderYear', None)
            if uuid is not None:
                return queryset.filter(uuid=uuid)
            if order_year is not None:
                return queryset.filter(date_bill__year=order_year)
            return queryset
        if request.user.is_authenticated:
            contact = Contact.objects.filter(user_ptr=request.user)
            if uuid is not None:
                result = queryset.filter(uuid=uuid)
            if contact:
                company = contact[0].company
                result = OrderDetail.objects.filter(state__isnull=True, company=company)
        else:
            result = OrderDetail.objects.filter(state__isnull=True, session=request.session.session_key)

        if result:
            return result
        else:
            new_cart = OrderDetail.create_new_order(request)
            return OrderDetail.objects.filter(uuid=new_cart.uuid)


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
            return Address.objects.filter(contact__in=Contact.objects.filter(session=self.request.session.session_key))


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
    queryset = OrderDetail.objects.all()
    serializer_class = OrderShipmentSerializer

    def create(self, request):
        order_serializer = OrderShipmentSerializer(data=request.data)
        if order_serializer.is_valid():
            order = request.data['order']
            order_details = OrderDetail.objects.get(uuid=order, is_send=False)

            shipment_address = Address.objects.get(id=request.data['shipment'])
            billing_address = Address.objects.get(id=request.data['billing'])
            order_details.shipment_address = shipment_address
            order_details.billing_address = billing_address
            order_details.save()
            return Response(order_serializer.data, status=status.HTTP_200_OK)
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
            queryset = queryset.filter(order_detail__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset = queryset.filter(order_detail__session=self.request.session.session_key)
        return queryset

    def update(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super(OrderItemViewSet, self).update(request, *args, **kwargs)
        instance = self.get_object()
        stock_sufficient, curr_stock = instance.product.product.is_stock_sufficient(instance.order_detail)
        new_items = int(request.data.get('count')) - instance.count

        if int(request.data.get('count')) > instance.product.product.max_items_per_order:
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
            queryset.filter(order_detail__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order_detail__session=self.request.session.session_key)
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
            queryset.filter(order_detail__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order_detail__session=self.request.session.session_key)
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
            queryset.filter(order_detail__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order_detail__session=self.request.session.session_key)
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
            queryset.filter(order_detail__company=Company.objects.get(contact__user_ptr=self.request.user))
        else:
            queryset.filter(order_detail__session=self.request.session.session_key)
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


class CompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Product.objects.all()
    serializer_class = BasicProductSerializer

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return FullProductSerializer
        return BasicProductSerializer

class ProductCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductAttributeTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductAttributeType.objects.all()
    serializer_class = ProductAttributeTypeSerializer


class ProductAttributeTypeInstanceViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductAttributeTypeInstance.objects.all()
    serializer_class = ProductAttributeTypeInstanceSerializer


class ProductSubItemViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductSubItem.objects.all()
    serializer_class = ProductSubItemSerializer


class ProductImageViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class ProductImageViewSetForProduct(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return super(ProductImageViewSetForProduct, self).get_queryset().filter(product=self.kwargs['id'])


class OrderStateViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = OrderState.objects.all()
    serializer_class = OrderStateSerializer


class FileExtensionItemViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = FileExtensionItem.objects.all()
    serializer_class = FileExtensionItemSerializer


class SelectItemViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = SelectItem.objects.all()
    serializer_class = SelectItemSerializer


class OrderItemStateViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = OrderItemState.objects.all()
    serializer_class = OrderItemStateSerializer


class IndividualOfferViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = IndividualOffer.objects.all()
    serializer_class = IndividualOfferSerializer


class PercentageDiscountViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = PercentageDiscount.objects.all()
    serializer_class = PercentageDiscountSerializer


class FixedAmountDiscountViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = FixedAmountDiscount.objects.all()
    serializer_class = FixedAmountDiscountSerializer


class WorkingTimeSerializerViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = WorkingTime.objects.all()
    serializer_class = WorkingTimeSerializer
