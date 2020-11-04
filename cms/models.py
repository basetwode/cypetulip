from enum import Enum

from django.db import models
# Create your models here.
from tinymce import HTMLField
from django.utils.translation import ugettext_lazy as _


from mediaserver.upload import fs, public_files_upload_handler


class PredefinedPages(Enum):
    PRIVACY_POLICY = _('Privacy Policy')
    GENERAL_BUSINESS_TERMS = _('General business terms')
    CANCELLATION_POLICY = _('Cancellation policy')
    LEGAL = _('Legal')


class Page(models.Model):
    page_name = models.CharField(max_length=30)
    position = models.IntegerField()
    is_enabled = models.BooleanField(default=True)
    link = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.page_name


class Section(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    content = HTMLField('Content')
    picture = models.FileField(default=None, null=True, blank=True,
                               upload_to=public_files_upload_handler,
                               storage=fs)


class CSSSetting(models.Model):
    main_color = models.CharField(max_length=6)
    second_color = models.CharField(max_length=6)
