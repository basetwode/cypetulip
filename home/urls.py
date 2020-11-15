"""main URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import home
    2. Add a URL to urlpatterns:  path('', home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.views.generic import RedirectView

from billing import urls as billing_urls
from cms import urls as cms_urls
from management import urls as admin_urls, rest
from mediaserver import urls as media_urls
from payment import urls as payment_urls
from permissions import urls as perm_urls
from shop import urls as shop_urls
from accounting import urls as accounting_urls
from shipping import urls as shipping_urls

# from Accounting import urls as accounting_urls
# from home import settings
from shop.authentification.views import PasswordResetViewSmtp

admin.autodiscover()

from filebrowser.sites import site

site.directory = "public/"

from django.core.files.storage import default_storage

site.storage = default_storage

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api/v1/', include(rest.router.urls)),
    url(r'^admin/filebrowser/', site.urls),
    url(r'^$', RedirectView.as_view(url='/cms/home/')),
    url(r'^admin/', admin.site.urls),
    url(r'^management/', include(admin_urls.urlpatterns)),
    url(r'^media/', include(media_urls.urlpatterns)),
    url(r'^cms/', include(cms_urls.urlpatterns)),
    url(r'^shop/', include(shop_urls, namespace='shop')),
    url(r'^permissions/', include(perm_urls.urlpatterns)),
    url(r'^billing/', include(billing_urls.urlpatterns)),
    url(r'^payment/', include(payment_urls, namespace='payment')),
    url(r'^accounting/', include(accounting_urls, namespace='accounting')),
    url(r'^shipping/', include(shipping_urls, namespace='shipping')),

    url(r'^password_reset/$', PasswordResetViewSmtp.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[\S0-9_.-\\s\- ]*)/(?P<token>[\S0-9_.-\\s\- ]*)/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^password_change/$', auth_views.PasswordChangeView.as_view(), name='password_change'),
    url(r'^password_change/done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]

# if settings.DEBUG:
#     settings.INSTALLED_APPS += ('django_uwsgi',)
#     urlpatterns += url(r'^admin/uwsgi/',include('django_uwsgi.urls'))
