from django.contrib import admin

from rma.models import *

# Register your models here.


admin.site.register(ReturnMerchandiseAuthorizationConfig)
admin.site.register(ReturnMerchandiseAuthorizationShipper)
admin.site.register(ReturnMerchandiseAuthorizationState)
admin.site.register(ReturnMerchandiseAuthorization)
admin.site.register(ReturnMerchandiseAuthorizationItem)