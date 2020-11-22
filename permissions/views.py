from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class PermissionDeniedView(TemplateView):
    template_name = '403.html'
