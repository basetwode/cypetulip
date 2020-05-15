from django.db import models


class Continent(models.Model):
    name = models.CharField(max_length=30)


class Country(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    continent = models.ForeignKey(
        Continent, on_delete=models.CASCADE, null=True, blank=True, related_name='continent', )


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
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
