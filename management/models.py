from django.db import models

from mediaserver.upload import public_files_upload_handler, fs


class MailSettings(models.Model):
    smtp_server = models.CharField(max_length=100)
    smtp_port = models.IntegerField()
    smtp_user = models.CharField(max_length=100)
    smtp_password = models.CharField(max_length=100)
    stmp_use_tls = models.BooleanField(max_length=100)
    smtp_default_from = models.CharField(max_length=100)


class LdapSettings(models.Model):
    ldap_server = models.CharField(max_length=100)
    ldap_port = models.IntegerField()
    ldap_user = models.CharField(max_length=100)
    ldap_password = models.CharField(max_length=100)
    ldap_use_tls = models.BooleanField(max_length=100)
    ldap_user_filter = models.CharField(max_length=1000)
    ldap_group_filter = models.CharField(max_length=1000)


class LegalSettings(models.Model):
    company_name = models.CharField(max_length=100)
    street = models.CharField(max_length=40, default=None)
    number = models.CharField(max_length=5, default=None)
    zipcode = models.CharField(max_length=5, default=None)
    city = models.CharField(max_length=100, default=None)
    phone = models.CharField(max_length=50, default=None)
    tax_number = models.CharField(max_length=50, default=None)
    register_number = models.CharField(max_length=50, default=None)
    logo = models.FileField(default=None, null=True, blank=True,
                            upload_to=public_files_upload_handler, storage=fs)
