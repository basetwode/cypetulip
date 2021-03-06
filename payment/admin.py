from django.contrib import admin

from payment.models.main import *

# Register your models here.
admin.site.register(PaymentMethod)
admin.site.register(Payment)
admin.site.register(PaymentProvider)
admin.site.register(PaymentDetail)
admin.site.register(CreditCard)
admin.site.register(CardType)
