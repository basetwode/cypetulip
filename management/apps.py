from __future__ import unicode_literals

from django.apps import AppConfig


class ManagementConfig(AppConfig):
    name = 'management'
    api = {}

    def ready(self):
        print("Loading management appconfig")
        try:
            from management.models import CacheSetting, LegalSetting
            cache_settings, _ = CacheSetting.objects.get_or_create()
            legal_settings, _ = LegalSetting.objects.get_or_create()
        except:
            pass
