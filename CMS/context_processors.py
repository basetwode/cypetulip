from CAD_Shop import settings
from CMS.models import Page

__author__ = ''


def get_version(request):
    return {
        'version': settings.VERSION
    }


def get_sites(request):
    pages = Page.objects.filter(is_enabled=True)
    return {
        'sites': pages
    }


def get_page_title(request):
    return {
        'title': settings.SHOP_NAME
    }

