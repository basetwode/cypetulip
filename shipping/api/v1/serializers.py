from rest_framework import serializers

from shipping.models.main import OnlineShipment, PackageShipment, Package, Shipper, Country, Continent


class ContinentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Continent
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Country
        fields = '__all__'


class ShipperSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Shipper
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Package
        fields = '__all__'


class PackageShipmentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = PackageShipment
        fields = '__all__'


class OnlineShipmentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = OnlineShipment
        fields = '__all__'
