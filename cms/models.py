from django.db import models

# Create your models here.
from mediaserver.upload import public_files_upload_handler, fs


class Page(models.Model):
    page_name = models.CharField(max_length=30)
    position = models.IntegerField()
    is_enabled = models.BooleanField(default=True)
    link = models.CharField(max_length=20, null=True, blank=True)


class Section(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    content = models.CharField(max_length=4000)
    picture = models.FileField(default=None, null=True, blank=True,
                               upload_to=public_files_upload_handler,
                               storage=fs)


class CSSSetting(models.Model):
    main_color = models.CharField(max_length=6)
    second_color = models.CharField(max_length=6)
