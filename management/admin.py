from django.contrib import admin

# Register your models here.
from management.models.main import LegalSetting, MailSetting, LdapSetting, Footer, Header, CacheSetting, ShopSetting

admin.site.register(LegalSetting)
admin.site.register(MailSetting)
admin.site.register(LdapSetting)
admin.site.register(Header)
admin.site.register(Footer)
admin.site.register(CacheSetting)
admin.site.register(ShopSetting)
