import os
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.generic import View
from Home import settings
# Todo: check permissions and raise 401 AND check if file exists and if not raise 404 then
from Permissions.error_handler import raise_404
from Permissions.permissions import check_serve_perms

CONTENT_TYPES = {
    '.pdf': 'application/pdf', '.jpg': 'image/jpg', '.png': 'image/png',
    '.jpeg': 'image/jpg', '.zip': 'application/zip', '.svg': 'image/svg',
}


class ServeOrderFiles(View):
    hash = None
    file = None

    @check_serve_perms
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

    @check_serve_perms
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

    def get(self, request, file):
        path = os.path.join(settings.MEDIA_ROOT + '/public/', file)
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
