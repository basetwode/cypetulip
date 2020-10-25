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
    order_object = None

    def form_valid(self, form):
        response = super(NotifyCustomerUpdateView, self).form_valid(form)
        translation.activate('de')
        self.send_mail(self.contact, self.subject, self.text, {'contact': self.contact, 'order': self.order_object,
                                                               'object': self.object,
                                                               'host': self.request.META['HTTP_HOST']})
        return response


class NotifyCustomerCreateView(CreateView, EmailMixin):
    email_template = "mail/shipment_changed.html"
    contact = None
    subject = _("Your order has been shipped")
    text = ""
    order_object = None

    def form_valid(self, form):
        response = super(NotifyCustomerCreateView, self).form_valid(form)
        translation.activate('de')
        self.send_mail(self.contact, self.subject, self.text, {**self.get_context_data(), **{'contact': self.contact,
                                                                                             'object': self.object,
                                                                                             'host': self.request.META[
                                                                                                 'HTTP_HOST'],
                                                                                             'order': self.order_object}})
        return response
