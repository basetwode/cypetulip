from cms.models import Page
from home import settings
from management.models import LegalSetting

__author__ = ''


def get_version(request):
    return {
        'version': settings.VERSION
    }


def get_nav_sites(request):
    pages = Page.objects.filter(is_enabled=True, show_in_navigation=True).order_by('position')
    return {
        'sites_nav': pages
    }


def get_sites(request):
    pages = Page.objects.filter(is_enabled=True).order_by('position')
    return {
        'sites': pages
    }


def get_page_title(request):
    return {
        'title': settings.SHOP_NAME
    }


def get_legal_information(request):
    legal = LegalSetting.objects.first()

    return {
        'legal': legal
    }