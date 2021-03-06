# Register your models here.
from django.contrib import admin

from shipping.models.main import *

admin.site.register(Continent)
admin.site.register(Country)
admin.site.register(Region)
admin.site.register(Shipper)
admin.site.register(Package)
admin.site.register(Shipment)
