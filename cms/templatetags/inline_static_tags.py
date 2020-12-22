import posixpath
import re

from django import template
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.safestring import mark_safe

register = template.Library()

class CssUrlTransformer(object):
    SCHEMES = ('http://', 'https://', '/')
    URL_PATTERN = re.compile(r"""
        url\(
        \s*      # any amount of whitespace
        ([\'"]?) # optional quote
        (.*?)    # any amount of anything, non-greedily (this is the actual url)
        \1       # matching quote (or nothing if there was none)
        \s*      # any amount of whitespace
        \)""", re.VERBOSE)

    def __init__(self, name, path, content, base_url=None):
        self.name = name
        self.path = path
        self.content = content

        self.base_scheme_domain, self.base_url = self.parse_static_url(
            base_url or settings.STATIC_URL)
        self.url = '{0}/{1}'.format(self.base_url, posixpath.dirname(self.name))

    def parse_static_url(self, base_url):
        if base_url.startswith(('http://', 'https://', '//')):
            base_url_parts = base_url.split('/')

            scheme_domain = '/'.join(base_url_parts[:3])
            base_url = '/'.join(base_url_parts[3:])
        else:
            scheme_domain = None

        return scheme_domain, base_url.rstrip('/')

    def transform(self):
        return self.URL_PATTERN.sub(self.transform_url, self.content)

    def transform_url(self, match):
        return 'url({quote}{url}{quote})'.format(
            quote=match.group(1), url=self.resolve_url(match.group(2)))

    def resolve_url(self, url):
        # Skip base64, etc. and external or already absolute paths
        if url.startswith(('#', 'data:')) or url.startswith(self.SCHEMES):
            return url

        resolved_url = posixpath.normpath('/'.join([self.url, url]))
        if self.base_scheme_domain:
            resolved_url = '{0}/{1}'.format(self.base_scheme_domain, resolved_url.lstrip('/'))
        return resolved_url


def transform_css_urls(*args, **kwargs):
    return CssUrlTransformer(*args, **kwargs).transform()

def load_staticfile(name, postprocessor=None, fail_silently=False):
    if postprocessor:
        cache_key = '{0}:{1}.{2}'.format(
            name, postprocessor.__module__, postprocessor.__name__)
    else:
        cache_key = name

    if cache_key in load_staticfile._cache:
        return load_staticfile._cache[cache_key]

    if settings.DEBUG:
        # Dont access file via staticfile storage in debug mode. Not available
        # without collectstatic management command.
        path = find(name)
    else:
        # Ensure that we include the hashed version of the static file if
        # staticfiles storage uses the HashedFilesMixin.
        if hasattr(staticfiles_storage, 'stored_name'):
            name = staticfiles_storage.stored_name(name)

        if staticfiles_storage.exists(name):
            # get path if target file exists.
            path = staticfiles_storage.path(name)
        else:
            path = None

    if not path:
        if not fail_silently:
            raise ValueError('Staticfile not found for inlining: {0}'.format(name))
        return ''

    with open(path, 'r') as staticfile:
        content = staticfile.read()

    if postprocessor:
        content = postprocessor(name, path, content)

    if not settings.DEBUG:
        load_staticfile._cache[cache_key] = content

    return content

load_staticfile._cache = {}

@register.simple_tag
def inline_staticfile(name):
    return load_staticfile(name, fail_silently=not settings.DEBUG)


@register.simple_tag
def inline_style(name):
    return mark_safe(load_staticfile(
        name, transform_css_urls, fail_silently=not settings.DEBUG))


@register.simple_tag
def inline_javascript(name):
    return mark_safe(load_staticfile(name, fail_silently=not settings.DEBUG))