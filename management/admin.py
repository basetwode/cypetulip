from django.contrib import admin

from cms.models import *

# Register your models here.
from management.models import LegalSettings, MailSettings, LdapSettings

admin.site.register(LegalSettings)
admin.site.register(MailSettings)
admin.site.register(LdapSettings)
