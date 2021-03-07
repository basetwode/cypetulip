import datetime

from django.core.validators import MaxValueValidator
from django.db import models

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


class PaymentMethod(models.Model):
    name = models.CharField(max_length=30)
    details = models.CharField(max_length=500, default='')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE, blank=True, null=True)
    enabled = models.BooleanField(default=True, blank=True)


class CardType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class PaymentDetail(models.Model):
    order_detail = models.ForeignKey(OrderDetail, on_delete=models.CASCADE, null=True, blank=True)
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    user = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True)

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


class Bill(PaymentDetail):
    pass


class Prepayment(PaymentDetail):
    pass


class PayPal(PaymentDetail):
    paypal_order_id = models.CharField(max_length=70, blank=True, null=True, default="")
    paypal_transaction_id = models.CharField(max_length=70, blank=True, null=True, default="")
    paypal_payer_id = models.CharField(max_length=70, blank=True, null=True, default="")


class Payment(models.Model):
    is_paid = models.BooleanField()
    token = models.CharField(max_length=100)
    details = models.ForeignKey(PaymentDetail, on_delete=models.CASCADE)

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