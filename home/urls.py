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
    1. Import the include() function: from django.urls import include, re_path, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView, SpectacularAPIView

from accounting import urls as accounting_urls
from billing import urls as billing_urls
from cms import urls as cms_urls
from management import urls as admin_urls
from mediaserver import urls as media_urls
from payment import urls as payment_urls
from permissions import urls as perm_urls
from rma import urls as rma_urls
from shipping import urls as shipping_urls
from shop import urls as shop_urls
from shop.views.authentication_views import PasswordResetViewSmtp, LoginAuthenticationView

admin.autodiscover()

from filebrowser.sites import site

site.directory = "public/"

from django.core.files.storage import default_storage

site.storage = default_storage

urlpatterns = [
    re_path(r'^api-auth/', include('rest_framework.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    re_path(r'^admin/filebrowser/', site.urls),
    re_path(r'^$', RedirectView.as_view(url='/cms/home/')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^management/', include(admin_urls.urlpatterns)),
    re_path(r'^media/', include(media_urls.urlpatterns)),
    re_path(r'^cms/', include(cms_urls.urlpatterns)),
    re_path(r'^shop/', include(shop_urls, namespace='shop')),
    re_path(r'^permissions/', include(perm_urls, namespace='permissions')),
    re_path(r'^billing/', include(billing_urls.urlpatterns)),
    re_path(r'^payment/', include(payment_urls, namespace='payment')),
    re_path(r'^accounting/', include(accounting_urls, namespace='accounting')),
    re_path(r'^shipping/', include(shipping_urls, namespace='shipping')),
    re_path(r'^rma/', include(rma_urls, namespace='rma')),

    re_path(r'^password_reset/$', PasswordResetViewSmtp.as_view(), name='password_reset'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[\S0-9_.-\\s\- ]*)/(?P<token>[\S0-9_.-\\s\- ]*)/$',
            auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    re_path(r'^password_change/$', auth_views.PasswordChangeView.as_view(), name='password_change'),
    re_path(r'^password_change/done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    re_path(r'^login/$', LoginAuthenticationView.as_view(), name='login'),
]

# if settings.DEBUG:
#     settings.INSTALLED_APPS += ('django_uwsgi',)
#     urlpatterns += re_path(r'^admin/uwsgi/',include('django_uwsgi.urls'))
