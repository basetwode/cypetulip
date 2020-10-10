from django.shortcuts import render

__author__ = ''


def raise_404(request):
    return render(request, '404.html')


def raise_401(request, context):
    return render(request, '403.html', context)
