from django.db import models
from tinymce.models import HTMLField

from mediaserver.upload import rma_files_upload_handler, fs
from shipping.models.main import Shipper, Shipment

from shop.models.accounts import Address, Contact
from shop.models.orders import OrderItem, OrderDetail


class ReturnMerchandiseAuthorizationConfig(models.Model):
    retention_time = models.IntegerField(default=14, blank=True)
    enabled = models.BooleanField(default=True)
    auto_approve = models.BooleanField(default=False)
    return_address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True)


class ReturnMerchandiseAuthorizationShipper(models.Model):
    shipper = models.ForeignKey(Shipper, on_delete=models.CASCADE, blank=True, null=True)
    description = HTMLField(blank=True, null=True, default="")
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.shipper.name if self.shipper else 'Default'


class ReturnMerchandiseAuthorizationState(models.Model):
    name = models.CharField(max_length=20)
    initial = models.BooleanField(default=False)
    is_end_state = models.BooleanField(default=False)
    next_state = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_state', )
    cancel_rma_state = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='cancel_state', )


class ReturnMerchandiseAuthorization(models.Model):
    number = models.CharField(max_length=100)
    order = models.ForeignKey(OrderDetail, on_delete=models.CASCADE)
    shipment = models.ForeignKey(Shipment, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    date_opened = models.DateTimeField(auto_now_add=True)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True)
    shipper = models.ForeignKey(ReturnMerchandiseAuthorizationShipper, on_delete=models.SET_NULL, null=True)
    approval_file = models.FileField(default=None, null=True,
                                     upload_to=rma_files_upload_handler,
                                     storage=fs)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.number:
            self.number = self.order.returnmerchandiseauthorization_set.count()+1
        super(ReturnMerchandiseAuthorization, self).save(force_insert, force_update, using, update_fields)

class ReturnMerchandiseAuthorizationItem(models.Model):
    rma = models.ForeignKey(ReturnMerchandiseAuthorization, on_delete=models.CASCADE)
    state = models.ForeignKey(ReturnMerchandiseAuthorizationState, on_delete=models.SET_NULL, null=True)
    reason = models.CharField(max_length=2000, null=True, blank=True, default="")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False, blank=True, null=True)
    approval_date = models.DateTimeField(blank=True, null=True, default=None)
    approval_employee = models.ForeignKey(Contact, blank=True, null=True, default=None, on_delete=models.SET_NULL)