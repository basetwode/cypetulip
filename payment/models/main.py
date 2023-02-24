import datetime

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from shop.models.accounts import Contact
from shop.models.orders import OrderDetail

YEAR_CHOICES = [(r, r) for r in range(datetime.datetime.now().year, datetime.datetime.now().year + 11)]
MONTH_CHOICES = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)]
PAYMENTMETHOD_BILL_NAME = 'Bill'


class PaymentProvider(models.Model):
    api = models.CharField(max_length=100)
    user_name = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)
    use_sandbox = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.api

    class Meta:
        verbose_name = _('PaymentProvider')
        verbose_name_plural = _('PaymentProviders')


class PaymentMethod(models.Model):
    name = models.CharField(max_length=30)
    details = models.CharField(max_length=500, default='')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE, blank=True, null=True)
    enabled = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('PaymentMethod')
        verbose_name_plural = _('PaymentMethods')


class CardType(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = _('CardType')
        verbose_name_plural = _('CardTypes')

    def __str__(self):
        return self.name


class PaymentDetail(models.Model):
    order_detail = models.ForeignKey(OrderDetail, on_delete=models.CASCADE, null=True, blank=True)
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    user = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True)

    class Meta:
        verbose_name = _('PaymentDetail')
        verbose_name_plural = _('PaymentDetails')

    def delete(self, using=None, keep_parents=False):
        self.payment_set.delete()
        super(PaymentDetail, self).delete(using, keep_parents)


class CreditCard(PaymentDetail):
    card_type = models.ForeignKey(CardType, on_delete=models.CASCADE)
    name = models.CharField(max_length=70)
    card_number = models.CharField(max_length=20)
    expiry_year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    expiry_month = models.IntegerField(choices=MONTH_CHOICES, default=datetime.datetime.now().month)
    cvv = models.PositiveIntegerField(validators=[MaxValueValidator(999)])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('CreditCard')
        verbose_name_plural = _('CreditCards')


class Bill(PaymentDetail):
    class Meta:
        verbose_name = _('Bill')
        verbose_name_plural = _('Bills')


class Prepayment(PaymentDetail):
    class Meta:
        verbose_name = _('Prepayment')
        verbose_name_plural = _('Prepayments')


class PayPal(PaymentDetail):
    paypal_order_id = models.CharField(max_length=70, blank=True, null=True, default="")
    paypal_transaction_id = models.CharField(max_length=70, blank=True, null=True, default="")
    paypal_payer_id = models.CharField(max_length=70, blank=True, null=True, default="")

    def __str__(self):
        return self.paypal_payer_id

    class Meta:
        verbose_name = _('PayPal')
        verbose_name_plural = _('PayPal')


class Payment(models.Model):
    is_paid = models.BooleanField()
    token = models.CharField(max_length=100)
    details = models.ForeignKey(PaymentDetail, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk is None:
            for order_item in self.details.order_detail.orderitem_set.all():
                if hasattr(order_item.product, 'product'):
                    order_item.product.product.decrease_stock(order_item.count)
            # update order create date
            self.details.order_detail.send_order()

        models.Model.save(self, force_insert, force_update,
                          using, update_fields)
