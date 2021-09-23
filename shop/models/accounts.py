from django.contrib.auth.models import User as DjangoUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from mediaserver.upload import company_files_upload_handler, fs, rand_key


class Company(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    company_id = models.CharField(max_length=100, blank=True, null=True)
    customer_nr = models.IntegerField(blank=True, null=True, verbose_name=_('Customer Nr'))
    term_of_payment = models.IntegerField(default=10, verbose_name=_('Term of payment'))
    street = models.CharField(max_length=40, default=None, verbose_name=_('Street'))
    number = models.CharField(max_length=5, default=None, verbose_name=_('Number'))
    zipcode = models.CharField(max_length=5, default=None, verbose_name=_('Zipcode'))
    city = models.CharField(max_length=30, default=None, verbose_name=_('City'))
    logo = models.FileField(default=None, null=True, blank=True,
                            upload_to=company_files_upload_handler, storage=fs)

    class Meta:
        verbose_name_plural = _("Companies")
        verbose_name = _("Company")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.company_id is None or len(self.company_id) == 0:
            self.company_id = rand_key(12)
        if self.customer_nr is None:
            nr = (Company.objects.filter(customer_nr__isnull=False).order_by('customer_nr').last().customer_nr + 1) \
                if Company.objects.all().count() > 0 and Company.objects.filter(
                customer_nr__isnull=False).exists() else 1
            self.customer_nr = nr
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)

    def __str__(self):
        return self.name or ""


class Contact(DjangoUser):
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
        ('D', _('Others')),
    )
    session = models.CharField(max_length=40, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_('Company'))
    company_customer_nr = models.IntegerField(blank=True, null=True, verbose_name=_('Company Customer Nr'))
    title = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Title'))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name=_('Gender'))
    telephone = models.CharField(max_length=40, verbose_name=_('Telephone'))
    language = models.CharField(max_length=2, default='en', verbose_name=_('Language'))
    billing_mail = models.EmailField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.company) + ' - ' + self.last_name + ' ' + self.first_name + f" ({self.username})"

    def is_registered(self):
        return self.groups.filter(name="client").exists()

    def customer_nr(self):
        return "C" + str(self.company.customer_nr).rjust(7, "0") + str(self.company_customer_nr).rjust(3, "0")

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.company_customer_nr is None:
            nr = (Contact.objects.filter(company=self.company, company_customer_nr__isnull=False).order_by(
                'company_customer_nr').last().company_customer_nr + 1) \
                if Contact.objects.filter(company=self.company, company_customer_nr__isnull=False).exists() else 1
            self.company_customer_nr = nr
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)


class Address(models.Model):
    name = models.CharField(max_length=100, default="", blank=True, null=True)
    street = models.CharField(max_length=40, default=None, verbose_name=_('Street'))
    number = models.CharField(max_length=5, default=None, verbose_name=_('Number'))
    zipcode = models.CharField(max_length=5, default=None, verbose_name=_('Zipcode'))
    city = models.CharField(max_length=100, default=None, verbose_name=_('City'))
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, default=None, blank=True, null=True,
                                verbose_name=_('Contact'))

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _("Addresses")

    def get_name(self):
        return self.name + " " + (self.contact.first_name + " " +self.contact.last_name) if self.contact else ""

    def __str__(self):
        return self.contact.__str__() + " | " + self.name


class WorkingTime(models.Model):
    employee = models.ForeignKey(Contact, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('WorkingTime')
        verbose_name_plural = _('WorkingTimes')
