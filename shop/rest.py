from rest_framework import viewsets, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from shop.models import Address, Contact, Company


class CompanySerializer(serializers.ModelSerializer):

    def create(self, request):
        return Company.objects.create(**request)

    class Meta:
        model = Company
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    def create(self, request):
        return Contact.objects.create(**request)

    class Meta:
        model = Contact
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()

    def create(self, request):
        contact = request.pop('contact', None)
        if contact:
            company = contact.pop('company', None)
            if company:
                company = Company.objects.get_or_create(**company)[0]
                contact['company'] = company
                contact = Contact.objects.get_or_create(**contact)[0]
                request['contact'] = contact
        return Address.objects.create(**request)

    class Meta:
        model = Address
        fields = '__all__'


###############################################################


class AccountViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def create(self, request):
        """
        Create a new account based on contact, company and address.
        """
        if request.method == 'POST':
            address_serializer = AddressSerializer(data=request.data['address'])
            if address_serializer.is_valid():
                address_serializer.save()
                return Response(address_serializer.data)
            else:
                return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            raise NotFound
