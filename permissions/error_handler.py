from django.shortcuts import render

__author__ = ''


def raise_404(request):
    return render(request, 'errors/404.html')


def raise_401(request, context):
    return render(request, 'errors/401.html', context)
