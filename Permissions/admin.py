from django.contrib import admin
from Permissions.models import *
# Register your models here.
admin.site.register(AppPermission)
admin.site.register(App)
admin.site.register(AppUrl)
admin.site.register(AppUrlPermission)