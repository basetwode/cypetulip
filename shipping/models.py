from django.db import models

from mediaserver.upload import fs, shipment_files_upload_handler
from shop.models import OrderDetail


class Continent(models.Model):
    name = models.CharField(max_length=30)


class Country(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    continent = models.ForeignKey(
        Continent, on_delete=models.CASCADE, null=True, blank=True, related_name='continent', )

    class Meta:
        verbose_name_plural = "Countries"


class Region(models.Model):
    name = models.CharField(max_length=30)
    countries = models.CharField(max_length=30)


class Shipper(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, )
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, )


class Package(models.Model):
    name = models.CharField(max_length=20)
    price = models.CharField(max_length=20)
    weight = models.BooleanField(default=False)
    tracking_code = models.CharField(max_length=60)
    shipper = models.ForeignKey(
        Shipper, on_delete=models.CASCADE, null=True, blank=True, related_name='shipper', )


class Shipment(models.Model):
    order = models.ForeignKey(OrderDetail, on_delete=models.SET_NULL, null=True, blank=True, )
    date_shipped = models.DateTimeField(auto_now_add=True)


class PackageShipment(Shipment):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)


class OnlineShipment(Shipment):
    file = models.FileField(default=None, null=True,
                            upload_to=shipment_files_upload_handler,
                            storage=fs)
    file_name = models.CharField(max_length=40, blank=True)
