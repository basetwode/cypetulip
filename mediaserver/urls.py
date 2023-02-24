from django.urls import re_path
from django.views.decorators.cache import never_cache

from mediaserver.views import (ServeCompanyFiles, ServeOrderFiles,
                               ServePublicFiles, ServeVersionFiles)

__author__ = ''

urlpatterns = [
    re_path(r"^orders/(?P<hash>[a-zA-Z0-9_.-]+)/(?P<file>([a-zA-Z0-9_.-]|\W)+)$",
            never_cache(ServeOrderFiles.as_view()),
            name="order_files"),
    re_path(r"^company/(?P<hash>[a-zA-Z0-9_.-]+)/(?P<file>([a-zA-Z0-9_.-]|\W)+)$",
            never_cache(ServeCompanyFiles.as_view()),
            name="company_files"),
    re_path(r"^public/(?P<file>[a-zA-Z0-9_.-]+)$", ServePublicFiles.as_view(),
            name="public_files"),
    re_path(r"^_versions/(?P<file>[a-zA-Z0-9_.-]+)$", ServeVersionFiles.as_view(),
            name="public_thumbnails"),
]
