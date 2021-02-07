from django.contrib import admin

# Register your models here.
from management.models.models import LegalSetting, MailSetting, LdapSetting, Footer, Header, CacheSetting

admin.site.register(LegalSetting)
admin.site.register(MailSetting)
admin.site.register(LdapSetting)
admin.site.register(Header)
admin.site.register(Footer)
admin.site.register(CacheSetting)
