import re

from compressor.filters import CallbackOutputFilter
from rcssmin import cssmin


def compress(css, **kwargs):
    capture_svg = re.compile(r'url\("(data:image/svg.*?svg%3[Ee])\"\)')
    data_urls = re.findall(capture_svg, css)
    for data_url in data_urls:
        css = css.replace(data_url, data_url.replace(' ', '%20'))
    css = cssmin(css, **kwargs)
    return css


class CSSMinFilter(CallbackOutputFilter):
    callback = 'cms.compressor.compress'

