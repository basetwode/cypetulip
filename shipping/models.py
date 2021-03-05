from django.db import models
from django.utils.translation import ugettext_lazy as _

from mediaserver.upload import fs, shipment_files_upload_handler
from shop.models.orders import OrderDetail, OrderItem


class Continent(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name = _('Continent')


class Country(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    continent = models.ForeignKey(
        Continent, on_delete=models.CASCADE, null=True, blank=True, related_name='continent',
        verbose_name=_('Continent'))

    class Meta:
        verbose_name_plural = "Countries"
        verbose_name = _('Country')


class Region(models.Model):
    name = models.CharField(max_length=30)
    countries = models.CharField(max_length=30, verbose_name=_('Countries'))


class Shipper(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, )
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, )

    class Meta:
        verbose_name_plural = _('Shippers')
        verbose_name = _('Shipper')


class Package(models.Model):
    name = models.CharField(max_length=20, verbose_name=_('Name'))
    price = models.CharField(max_length=20, verbose_name=_('Price'))
    weight = models.CharField(max_length=20, verbose_name=_('Weight'))
    tracking_code = models.CharField(max_length=60, verbose_name=_('Tracking code'))
    shipper = models.ForeignKey(
        Shipper, on_delete=models.CASCADE, null=True, blank=True, related_name='shipper', verbose_name=_('Shipper'))

    class Meta:
        verbose_name = _('Package')


class Shipment(models.Model):
    order = models.ForeignKey(OrderDetail, on_delete=models.SET_NULL, null=True, blank=True, )
    date_shipped = models.DateTimeField(auto_now_add=True)
    order_items_shipped = models.ManyToManyField(OrderItem, blank=True)

    class Meta:
        verbose_name = _('Shipment')


class PackageShipment(Shipment):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)


class OnlineShipment(Shipment):
    file = models.FileField(default=None, null=True,
                            upload_to=shipment_files_upload_handler,
                            storage=fs)
    file_name = models.CharField(max_length=40, blank=True)
