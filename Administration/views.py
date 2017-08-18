from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View


class AdminView(View):

    def get(self, request):
        # <view logic>
        return HttpResponse('AdminView')

    def post(self, request):
        # <view logic>
        return HttpResponse('result')


class SettingsView(View):

    def get(self, request):
        # <view logic>
        return HttpResponse('SettingsView')

    def post(self, request):
        # <view logic>
        return HttpResponse('result')


class SettingsDetailView(View):
    app_name = None

    def get(self, request, app_name):
        # <view logic>
        return HttpResponse('SettingsDetailView')

    def post(self, request):
        # <view logic>
        return HttpResponse('result')

    def get_app(self, queryset=None):
        return queryset.get(app_name=self.app_name)