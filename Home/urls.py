"""main URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

#from Accounting import urls as accounting_urls
from Home import settings
from MediaServer import urls as media_urls
from Shop import urls as shop_urls
from Permissions import urls as perm_urls
from CMS import urls as cms_urls
from Billing import urls as billing_urls
from Administration import urls as admin_urls
from Payment import urls as payment_urls
admin.autodiscover()


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/cms/Home/')),
    url(r'^admin/', admin.site.urls),
    url(r'^administration/', include(admin_urls.urlpatterns)),
   # url(r'^accounting/', include(accounting_urls.urlpatterns)),
    url(r'^media/', include(media_urls.urlpatterns)),
    url(r'^shop/', include(shop_urls.urlpatterns)),
    url(r'^permissions/', include(perm_urls.urlpatterns)),
    url(r'^cms/', include(cms_urls.urlpatterns)),
    url(r'^billing/', include(billing_urls.urlpatterns)),
    url(r'^payment/', include(payment_urls.urlpatterns)),
]

# if settings.DEBUG:
#     settings.INSTALLED_APPS += ('django_uwsgi',)
#     urlpatterns += url(r'^admin/uwsgi/',include('django_uwsgi.urls'))
