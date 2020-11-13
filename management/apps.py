from __future__ import unicode_literals

from django.apps import AppConfig



class ManagementConfig(AppConfig):
    name = 'management'

    def ready(self):
        pass