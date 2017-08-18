from Administration.views import SettingsDetailView, SettingsView, AdminView
from django.conf.urls import url

__author__ = ''


urlpatterns = [
    url(r'^$', AdminView.as_view()),
    url(r'^settings/$', SettingsView.as_view()),
    url(r"^settings/(?P<app_name>[a-zA-Z0-9_.-]+)$", SettingsDetailView.as_view())
]