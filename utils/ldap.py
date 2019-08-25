from django.db import models


class Ldap(models.Model):
    server_uri = models.CharField(max_length=100)
    bind_dn = models.CharField(max_length=100)
    bind_password = models.CharField(max_length=100)
    user_search = models.CharField(max_length=100)
    group_search = models.BooleanField(max_length=100)
    group_require = models.CharField(max_length=1000)
    group_deny = models.CharField(max_length=1000)
    user_attr_map = models.CharField(max_length=1000)
    user_flag_by_groups = models.CharField(max_length=1000)
