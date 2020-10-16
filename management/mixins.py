from django.utils import translation
from django.views.generic import UpdateView, CreateView
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import View

from utils.mixins import EmailMixin


class NotifyCustomerUpdateView(UpdateView, EmailMixin):
    email_template = "mail/new_shipment.html"
    contact = None
    subject = _("Shipment for your order has changed")
    text = ""

    def form_valid(self, form):
        translation.activate('de')
        self.send_mail(self.contact, self.subject, self.text, {'contact': self.contact})
        return super(NotifyCustomerUpdateView, self).form_valid(form)


class NotifyCustomerCreateView(CreateView, EmailMixin):
    email_template = "mail/shipment_changed.html"
    contact = None
    subject = _("Your order has been shipped")
    text = ""

    def form_valid(self, form):
        translation.activate('de')
        self.send_mail(self.contact, self.subject, self.text, {'contact': self.contact})
        return super(NotifyCustomerCreateView, self).form_valid(form)