from rest_framework import viewsets, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from shop.models import Address, Contact, Company, Order, OrderDetail
from shop.utils import create_hash


class CompanySerializer(serializers.ModelSerializer):
    def create(self, request):
        return Company.objects.create(**request)

    class Meta:
        model = Company
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    def create(self, request):
        company = request.pop('company', None)
        if company:
            company = Company.objects.create(**company)
            request['company'] = company
        return Contact.objects.create(**request)

    class Meta:
        model = Contact
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):

    def create(self, request):
        return Address.objects.create(**request)

    class Meta:
        model = Address
        fields = '__all__'


class OrderShipmentSerializer(serializers.Serializer):
    order = serializers.CharField(max_length=200, required=False)
    shipment = serializers.CharField()


###############################################################


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
                    address.contact = Contact.objects.get(user=self.request.user)
                    address.save()
                    return Response(address_serializer.data)
                else:
                    return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                address_serializer = AddressSerializer(data=request.data['address'])
                contact_serializer = ContactSerializer(data=request.data['contact'])
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


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        """
        This view should return a list of all addresses
        for the currently authenticated user.
        """
        if self.request.user.is_authenticated:
            user = self.request.user
            contact = Contact.objects.get(user=user)
            return Address.objects.filter(contact=contact)
        else:
            raise NotFound()


class ContactViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_queryset(self):
        """
        This view should return a contact for the authenticated user
        for the currently authenticated user.
        """
        if self.request.user.is_authenticated:
            user = self.request.user
            return Contact.objects.filter(user=user)
        else:
            raise NotFound()


class DeliveryViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    queryset = Order.objects.all()

    def create(self, request):
        order_serializer = OrderShipmentSerializer(data=request.data)
        if order_serializer.is_valid():
            order = request.data['order']
            _order = Order.objects.filter(order_hash=order, is_send=False)
            order_details = OrderDetail.objects.get(order_number=order)
            if _order.count() > 0:
                token = create_hash()
                shipment_address = Address.objects.get(id=request.data['shipment'])
                order_details.shipment_address = shipment_address
                order_details.save()
                ord = _order[0]
                ord.token = token
                ord.save()
                return Response(order_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
