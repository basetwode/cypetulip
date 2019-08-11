from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.template import loader
from django.template import RequestContext

__author__ = ''


def raise_404(request):
    c = RequestContext(request, {})
    t = loader.get_template('errors/404.html')
    return HttpResponseNotFound(t.render(c.flatten()))


def raise_401(request, context={}):
    c = RequestContext(request, context)
    t = loader.get_template('errors/401.html')
    return HttpResponseForbidden(t.render(c.flatten()))
