from __future__ import unicode_literals

import datetime

from django.core.validators import MaxValueValidator
from django.db import models

from shop.models import Contact, Order

# Create your models here.


YEAR_CHOICES = [(r, r) for r in range(datetime.datetime.now().year, datetime.datetime.now().year + 11)]
MONTH_CHOICES = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)]


# Details for logging in to the api
class PaymentProvider(models.Model):
    api = models.CharField(max_length=100)
    user_name = models.CharField(max_length=40)
    secret = models.CharField(max_length=50)


# method like paypal and sofort
class PaymentMethod(models.Model):
    name = models.CharField(max_length=30)
    details = models.CharField(max_length=500, default='')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE, blank=True, null=True)


class CardType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class PaymentDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    user = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True)


# TODO: a credit card should belong to an user or company
class CreditCard(PaymentDetail):
    card_type = models.ForeignKey(CardType, on_delete=models.CASCADE)
    name = models.CharField(max_length=70)
    card_number = models.CharField(max_length=20)
    expiry_year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    expiry_month = models.IntegerField(choices=MONTH_CHOICES, default=datetime.datetime.now().month)
    cvv = models.PositiveIntegerField(validators=[MaxValueValidator(999)])


class Bill(PaymentDetail):
    pass


# The object for orders to determine wether order has been paid or not and stuff
class Payment(models.Model):
    is_paid = models.BooleanField()
    token = models.CharField(max_length=30)
    details = models.ForeignKey(PaymentDetail, on_delete=models.CASCADE)
