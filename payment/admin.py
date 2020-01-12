from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(PaymentMethod)
admin.site.register(Payment)
admin.site.register(PaymentProvider)
admin.site.register(PaymentDetails)
admin.site.register(CreditCard)
admin.site.register(CardType)
