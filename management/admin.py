from django.contrib import admin

# Register your models here.
from management.models import LegalSetting, MailSetting, LdapSetting, Footer, Header

admin.site.register(LegalSetting)
admin.site.register(MailSetting)
admin.site.register(LdapSetting)
admin.site.register(Header)
admin.site.register(Footer)
