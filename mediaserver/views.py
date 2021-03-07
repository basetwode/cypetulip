import os

from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.generic import View

from home import settings
# Todo: check permissions and raise 401 AND check if file exists and if not raise 404 then
from permissions.error_handler import raise_404
from permissions.views.mixins import PermissionOwnsObjectMixin
from shop.models.orders import OrderDetail

CONTENT_TYPES = {
    '.pdf': 'application/pdf', '.jpg': 'image/jpg', '.png': 'image/png',
    '.jpeg': 'image/jpg', '.zip': 'application/zip', '.svg': 'image/svg',
}


class ServeOrderFiles(PermissionOwnsObjectMixin, View):
    model = OrderDetail
    slug_field = "uuid"
    slug_url_kwarg = "hash"
    field_name = "contact"
    hash = None
    file = None

    def get(self, request, hash, file):
        path = os.path.join(settings.MEDIA_ROOT + '/orders/', hash, file)
        if os.path.isfile(path):
            file_extension = os.path.splitext(path)[1].lower()
            image_data = open(path, "rb").read()
            content_type = CONTENT_TYPES.get(file_extension)
            if not content_type:
                content_type = 'application/' + file_extension[1:]
            return HttpResponse(image_data, content_type=content_type)
        return raise_404(request)

    def post(self, request):
        return HttpResponseNotAllowed('GET')


class ServeCompanyFiles(View):
    hash = None
    file = None

    def get(self, request, hash, file):
        path = os.path.join(settings.MEDIA_ROOT + '/company/', hash, file)
        if os.path.isfile(path):
            file_extension = os.path.splitext(path)[1].lower()
            image_data = open(path, "rb").read()
            content_type = CONTENT_TYPES.get(file_extension)
            if not content_type:
                content_type = 'application/' + file_extension[1:]
            return HttpResponse(image_data, content_type=content_type)
        return raise_404(request)

    def post(self, request):
        return HttpResponseNotAllowed('GET')


class ServePublicFiles(View):
    file = None
    path = '/public/'

    def get(self, request, file):
        path = os.path.join(settings.MEDIA_ROOT + self.path, file)
        if os.path.isfile(path):
            file_extension = os.path.splitext(path)[1].lower()
            image_data = open(path, "rb").read()
            content_type = CONTENT_TYPES.get(file_extension)
            if not content_type:
                content_type = 'application/' + file_extension[1:]
            return HttpResponse(image_data, content_type=content_type)
        return raise_404(request)

    def post(self, request):
        return HttpResponseNotAllowed('GET')


class ServeVersionFiles(ServePublicFiles):
    path = '/_versions/'