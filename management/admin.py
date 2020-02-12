from django.contrib import admin

# Register your models here.
from management.models import LegalSetting, MailSetting, LdapSetting

admin.site.register(LegalSetting)
admin.site.register(MailSetting)
admin.site.register(LdapSetting)
