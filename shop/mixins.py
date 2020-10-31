from django.db.models import When, FloatField, Case, Count, F
from django.db.models.functions import Cast
from django.utils import translation
from django.views import View
from django.views.generic import CreateView
from django.utils.translation import ugettext_lazy as _

from billing.utils import calculate_sum, Round
from management.models import MailSetting, LegalSetting
from shop.models import Contact, OrderDetail, OrderItem
from utils.mixins import EmailMixin
from utils.views import CreateUpdateView


class TaxView(View):

    def add_tax_to_product(self, products):
        products.annotate(tprice=Round((Case(
            When(special_price=False, then='price'),
            When(special_price__gte=0, then='special_price'),
            default='price',
            output_field=FloatField(),
        ) * (F('tax') + 1), FloatField(), 2)))


class EmailNotifyStaffView(EmailMixin, View):
    email_template = "mail/new_individual_offer_request.html"
    subject = _("New individual offer request")
    text = ""
    object = None

    def notify(self):
        mail_settings = MailSetting.objects.first()
        contact = Contact()
        contact.email = mail_settings.contact_new_order
        self.send_mail(contact, self.subject, self.text, {'contact': contact,
                                                          'files': None,
                                                          'object': self.object,
                                                          'host': self.request.META[
                                                              'HTTP_HOST']})


class EmailConfirmView(EmailMixin, View):
    email_template = "mail/new_order_client.html"
    subject = _("Your order")
    text = ""
    object = None

    def notify_client(self, contact):
        translation.activate('de')
        order_detail = OrderDetail.objects.filter(order=self.object)
        self.object.unique_nr = order_detail[0].unique_nr()
        self.subject += f" {order_detail[0].unique_nr()}"

        order_items = OrderItem.objects.filter(order=self.object)
        total = calculate_sum(order_items, True)

        self.send_mail(contact, self.subject, self.text, {'contact': contact,
                                                          'order': self.object,
                                                          'object': self.object,
                                                          'total': total,
                                                          'host': self.request.META[
                                                              'HTTP_HOST']})

    def notify_staff(self):
        # todo: send mail upon bill
        mail_setting = MailSetting.objects.first()
        translation.activate('de')
        self.email_template = "mail/new_order_staff.html"
        self.subject = _("New order has been placed")
        self.text = ""

        staff_contact = Contact()
        staff_contact.email = mail_setting.contact_new_order
        order_detail = OrderDetail.objects.filter(order=self.object)
        self.object.unique_nr = order_detail[0].unique_nr()
        order_items = OrderItem.objects.filter(order=self.object)
        total = calculate_sum(order_items, True)
        self.subject += f" {order_detail[0].unique_nr()}"

        self.send_mail(staff_contact,
                       self.subject, self.text, {'contact': staff_contact,
                                                 'order': self.object,
                                                 'object': self.object,
                                                 'total': total,
                                                 'host': self.request.META[
                                                     'HTTP_HOST']})


class WizardView(CreateUpdateView):
    template_name = 'generic-create-form.html'
    page_title = ''

    def get_back_url(self):
        return None


    def get_success_url(self):
        super(WizardView, self).get_success_url()

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs),
                **{'return_url': self.get_back_url(),
                   'page_title': self.page_title}}

    def get_parent_id(self):
        return self.kwargs['parent_id'] if 'parent_id' in self.kwargs else None


class RepeatableWizardView(WizardView):
    parent_key = ''
    self_url = ''
    delete_url = ''


    def get_next_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs),
                **{'next_url': self.get_next_url(),
                   'self_url': self.self_url,
                   'delete_url': self.delete_url,
                   'parent_id': self.get_parent_id(),
                   'object_list': self.model.objects.filter(**{self.parent_key: self.get_parent_id()})}}
