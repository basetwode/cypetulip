from django.db import models
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from mediaserver.upload import public_files_upload_handler, fs


class MailSetting(models.Model):
    contact_new_order = models.EmailField(null=True, blank=True, default=None)
    smtp_server = models.CharField(max_length=100)
    smtp_port = models.IntegerField()
    smtp_user = models.CharField(max_length=100)
    smtp_password = models.CharField(max_length=100)
    stmp_use_tls = models.BooleanField(max_length=100)
    smtp_default_from = models.CharField(max_length=100)

    def __str__(self):
        return self.smtp_server

    class Meta:
        verbose_name = _('MailSetting')
        verbose_name_plural = _('MailSettings')


class LdapSetting(models.Model):
    ldap_server = models.CharField(max_length=100)
    ldap_port = models.IntegerField()
    ldap_user = models.CharField(max_length=100)
    ldap_password = models.CharField(max_length=100)
    ldap_use_tls = models.BooleanField(max_length=100)
    ldap_user_filter = models.CharField(max_length=1000)
    ldap_group_filter = models.CharField(max_length=1000)

    def __str__(self):
        return self.ldap_server

    class Meta:
        verbose_name = _('LdapSetting')
        verbose_name_plural = _('LdapSettings')


class ShopSetting(models.Model):
    google_recaptcha_publickey = models.CharField(max_length=100)
    google_recaptcha_privatekey = models.CharField(max_length=100)

    class Meta:
        verbose_name = _('ShopSetting')
        verbose_name_plural = _('ShopSettings')


class LegalSetting(models.Model):
    company_name = models.CharField(max_length=100)
    street = models.CharField(max_length=40, default=None, null=True, blank=True)
    number = models.CharField(max_length=5, default=None, null=True, blank=True)
    zipcode = models.CharField(max_length=5, default=None, null=True, blank=True)
    city = models.CharField(max_length=100, default=None, null=True, blank=True)
    phone = models.CharField(max_length=50, default=None, null=True, blank=True)
    mail = models.EmailField(null=True, blank=True, default=None)
    tax_number = models.CharField(max_length=50, default=None, null=True, blank=True,)
    register_number = models.CharField(max_length=50, default=None, null=True, blank=True,)
    logo = models.FileField(default=None, null=True, blank=True,
                            upload_to=public_files_upload_handler, storage=fs)
    iban = models.CharField(max_length=30, null=True, blank=True, default=None)
    bic = models.CharField(max_length=20, null=True, blank=True, default=None)
    account_holder = models.CharField(max_length=20, null=True, blank=True, default=None)
    cancellation_policy = HTMLField(null=True, blank=True, default=None)
    general_business_term = HTMLField(null=True, blank=True, default=None)
    privacy_policy = HTMLField(null=True, blank=True, default=None)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = _('LegalSetting')
        verbose_name_plural = _('LegalSettings')


class Layout(models.IntegerChoices):
    ONE_COLUMN = 1, _('One Column Layout')
    TWO_COLUMN = 2, _('Two Column Layout')
    THREE_COLUMN = 3, _('Three Column Layout')


class Header(models.Model):
    name = models.CharField(max_length=40, default='Standard', verbose_name=_('Name'))
    is_enabled = models.BooleanField(verbose_name=_('Is enabled'))
    language = models.CharField(max_length=2, default='en', verbose_name=_('Language'))
    layout = models.IntegerField(choices=Layout.choices, default=Layout.THREE_COLUMN, verbose_name=_('Layout'))
    content_column_one = HTMLField(_('Content Column One'), null=True, blank=True)
    content_column_two = HTMLField(_('Content Column Two'), null=True, blank=True)
    content_column_three = HTMLField(_('Content Column Three'), null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Header')
        verbose_name_plural = _('Headers')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        enabled_headers = Header.objects.filter(is_enabled=True, language=self.language).exclude(id=self.id)
        if enabled_headers:
            for header in enabled_headers:
                header.is_enabled = False
                header.save()
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)

    def delete(self, using=None, keep_parents=False):
        super(Header, self).delete(using, keep_parents)


class Footer(models.Model):
    name = models.CharField(max_length=40, default='Standard', verbose_name=_('Name'))
    is_enabled = models.BooleanField(verbose_name=_('Is enabled'))
    language = models.CharField(max_length=2, default='en', verbose_name=_('Language'))
    sitemap = models.BooleanField(verbose_name=_('Sitemap'))
    payment_methods = models.BooleanField(verbose_name=_('Payment methods'))
    layout = models.IntegerField(choices=Layout.choices, default=Layout.THREE_COLUMN, verbose_name=_('Layout'))
    content_column_one = HTMLField(_('Content Column One'), null=True, blank=True)
    content_column_two = HTMLField(_('Content Column Two'), null=True, blank=True)
    content_column_three = HTMLField(_('Content Column Three'), null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Footer')
        verbose_name_plural = _('Footers')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        enabled_footers = Footer.objects.filter(is_enabled=True, language=self.language).exclude(id=self.id)
        if enabled_footers:
            for footer in enabled_footers:
                footer.is_enabled = False
                footer.save()
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)

    def delete(self, using=None, keep_parents=False):
        super(Footer, self).delete(using, keep_parents)


class CacheSetting(models.Model):
    css_js_cache_enabled = models.BooleanField(verbose_name=_('Is CSS/JS cache enabled'), default=True)
    cache_clear_required = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('CacheSetting')
        verbose_name_plural = _('CacheSettings')
