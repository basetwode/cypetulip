from cms.models import Page
from home import settings
from management.models.models import LegalSetting, CacheSetting

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
        'title': LegalSetting.objects.first().company_name
    }


def get_legal_information(request):
    legal = LegalSetting.objects.first()

    return {
        'legal': legal
    }

def get_js_css_version(request):
    cache_settings = CacheSetting.objects.first()
    return cache_settings.current_version
