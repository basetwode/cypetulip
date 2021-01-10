from __future__ import unicode_literals

from django.apps import AppConfig



class ManagementConfig(AppConfig):
    name = 'management'

    def ready(self):
        try:
            from management.models import CacheSetting
            cache_settings,_ = CacheSetting.objects.get_or_create()
        except :
            pass