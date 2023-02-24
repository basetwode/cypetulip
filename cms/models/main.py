from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.
from tinymce.models import HTMLField

from mediaserver.upload import fs, public_files_upload_handler

PREDEFINED_PAGES = [
    ('privacy-policy', '/cms/privacy-policy'),
    ('general-business-terms', '/cms/general-business-terms'),
    ('cancellation-policy', '/cms/cancellation-policy'),
    ('legal', '/cms/legal'),
    ('contact', '/cms/contact'),
    ('products', '/shop/products'),
]


class Page(models.Model):
    page_id = models.CharField(max_length=100, default="", editable=False)
    page_name = models.CharField(verbose_name=_('Page name'), max_length=30)
    position = models.IntegerField(default=0, blank=True, null=True)
    is_enabled = models.BooleanField(verbose_name=_('Is enabled'), default=True)
    link = models.CharField(verbose_name=_('URL Path'), max_length=200, null=True, blank=True, editable=False)
    show_in_navigation = models.BooleanField(verbose_name=_('Show in navigation'), default=False)
    is_predefined = models.BooleanField(verbose_name=_('Is predefined page'), default=False, editable=False)

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _("Pages")

    def __str__(self):
        return self.page_name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.is_predefined:
            self.page_id = self.page_name.lower().replace(" ", "-")
        # Only for initial creation
        if self.is_predefined and not self.page_name:
            self.page_name = self.page_id.replace("-", " ").capitalize()
        if not self.link or not self.page_id in self.link:
            self.link = '/cms/' + self.page_id

        models.Model.save(self, force_insert, force_update,
                          using, update_fields)


class Section(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    content = HTMLField(_('Content'))
    picture = models.FileField(verbose_name=_('Picture'), default=None, null=True, blank=True,
                               upload_to=public_files_upload_handler,
                               storage=fs)

    def __str__(self):
        return _('Section of ') + self.page.page_name

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')
