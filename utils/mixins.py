import threading
import time
from email.mime.image import MIMEImage

from django.core.checks import translation
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views import View

from management.models import LegalSetting
from shipping.models import OnlineShipment
from shop.models import Order


class EmailMixin:
    email_template = ''

    def get_template(self):
        return self.email_template

    def send_mail(self, receiver_user, subject, content, context):
        EmailThread(receiver_user, content, subject, context, self.get_template()).start()


class EmailThread(threading.Thread):
    def __init__(self, receiver_user, content, subject, context, email_template):
        self.subject = subject
        self.context = context
        self.content = content
        self.email_template = email_template
        self.receiver_user = receiver_user
        threading.Thread.__init__(self)

    def run(self):

        result = None
        tries = 0
        while (result is None or result is not 1) and tries < 5:
            try:
                print("Sending new email to " + self.receiver_user.email)
                legal = LegalSetting.objects.first()
                self.context['content'] = self.content
                self.context['legal'] = legal
                html_content = render_to_string(self.email_template, context=self.context)
                print(self.content)

                email = EmailMultiAlternatives('Subject', self.subject)
                email.subject = self.subject
                email.mixed_subtype = 'related'
                email.content_subtype = 'html'
                email.attach_alternative(html_content, "text/html")
                email.to = [self.receiver_user.email]

                logo_file = legal.logo.open("rb")
                try:
                    logo = MIMEImage(logo_file.read())
                    logo.add_header('Content-ID', '<{}>'.format(legal.logo.name))
                    email.attach(logo)
                finally:
                    logo_file.close()

                if self.context['files']:
                    for file_name, file in self.context['files'].items():
                        email.attach(file_name, file, )

                if isinstance(self.context['object'], OnlineShipment):
                    email.attach_file(self.context['object'].file.path)

                if isinstance(self.context['object'], Order):
                    for order_item in self.context['object'].orderitem_set.all():
                        product_file = order_item.product.product.product_picture.open("rb")
                        try:
                            product_img = MIMEImage(product_file.read())
                            product_img.add_header('Content-ID', '<{}>'
                                                   .format(order_item.product.product.product_picture.name))
                            email.attach(product_img)
                        finally:
                            product_file.close()

                print("from " + email.from_email)
                print("Sending mail")
                tries += 1
                result = email.send()
                print(result)
            except Exception as e:
                print(e)
                print("Error when sending mail... retrying")
                time.sleep(15)
        return result


class PaginatedFilterViews(View):
    def get_context_data(self, **kwargs):
        context = super(PaginatedFilterViews, self).get_context_data(**kwargs)
        if self.request.GET:
            querystring = self.request.GET.copy()
            if self.request.GET.get('page'):
                del querystring['page']
            context['querystring'] = querystring.urlencode()
        return context