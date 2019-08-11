from django.db import models


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
