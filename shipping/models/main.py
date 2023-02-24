from django.db import models
from django.utils.translation import gettext_lazy as _

from mediaserver.upload import shipment_files_upload_handler, fs
from shop.models.orders import OrderDetail, OrderItem


class Continent(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Continent')
        verbose_name_plural = _("Continents")


class Country(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    continent = models.ForeignKey(
        Continent, on_delete=models.CASCADE, null=True, blank=True, related_name='continent',
        verbose_name=_('Continent'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _("Countries")


class Region(models.Model):
    name = models.CharField(max_length=30)
    countries = models.CharField(max_length=30, verbose_name=_('Countries'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _("Regions")


class Shipper(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, )
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True, )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Shipper')
        verbose_name_plural = _('Shippers')


class Package(models.Model):
    name = models.CharField(max_length=20, verbose_name=_('Name'))
    price = models.CharField(max_length=20, verbose_name=_('Price'))
    weight = models.CharField(max_length=20, verbose_name=_('Weight'))
    tracking_code = models.CharField(max_length=60, verbose_name=_('Tracking code'))
    shipper = models.ForeignKey(
        Shipper, on_delete=models.CASCADE, null=True, blank=True, related_name='shipper', verbose_name=_('Shipper'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Package')
        verbose_name_plural = _('Packages')


class Shipment(models.Model):
    order = models.ForeignKey(OrderDetail, on_delete=models.SET_NULL, null=True, blank=True, )
    date_shipped = models.DateTimeField(auto_now_add=True)
    order_items_shipped = models.ManyToManyField(OrderItem, blank=True)

    def __str__(self):
        return self.order.uuid

    class Meta:
        verbose_name = _('Shipment')
        verbose_name_plural = _('Shipments')


class PackageShipment(Shipment):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('PackageShipment')
        verbose_name_plural = _("PackageShipments")


class OnlineShipment(Shipment):
    file = models.FileField(default=None, null=True,
                            upload_to=shipment_files_upload_handler,
                            storage=fs)
    file_name = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = _('OnlineShipment')
        verbose_name_plural = _("OnlineShipments")
