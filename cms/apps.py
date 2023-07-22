from __future__ import unicode_literals

from django.apps import AppConfig


class CmsConfig(AppConfig):
    name = 'cms'
    api = {}

    def ready(self):
        print("Loading cms appconfig")
        try:
            from cms.models.main import Page, PREDEFINED_PAGES

            pages = list(map(lambda c: {'page_name': c[0], 'link': c[1]}, PREDEFINED_PAGES))
            for ppage in pages:
                page, created = Page.objects.get_or_create(page_id=ppage['page_name'],
                                                           link=ppage['link'], is_predefined=True)
        except:
            print("DB not migrated")
