import threading
import time
from email.mime.image import MIMEImage

from django.core import mail
from django.core.checks import translation
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.views import View
from django.db import connections

from home import settings
from management.models import LegalSetting, MailSetting
from shipping.models import OnlineShipment
from shop.models import Order

class EmailLogMixin:

    def log(self, **kwargs):
        pass
        # log = CommunicationLog(
        #     contact=
        #     kwargs
        # )



class EmailMixin:
    email_template = ''

    def get_template(self):
        return self.email_template

    def connection(self):
        if MailSetting.objects.exists():
            mail_setting = MailSetting.objects.first()
            # Host for sending e-mail.
            settings.EMAIL_HOST = mail_setting.smtp_server
            # Port for sending e-mail.
            settings.EMAIL_PORT =  mail_setting.smtp_port
            settings.DEFAULT_FROM_EMAIL = mail_setting.smtp_default_from
            # Optional SMTP authentication information for EMAIL_HOST.
            settings.EMAIL_HOST_USER = mail_setting.smtp_user
            settings.EMAIL_HOST_PASSWORD = mail_setting.smtp_password
            settings.EMAIL_USE_TLS = mail_setting.stmp_use_tls
        return get_connection(
            host=settings.EMAIL_HOST,
            port= settings.EMAIL_PORT,
            username= settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
        )

    def send_mail(self, receiver_user, subject, content, context):
        mail_thread = EmailThread(receiver_user, content, subject, context, self.get_template(), self.connection())
        mail_thread.create_mail()
        mail_thread.start()

class EmailThread(threading.Thread):
    def __init__(self, receiver_user, content, subject, context, email_template, connection):
        super(EmailThread, self).__init__()
        self.subject = subject
        self.context = context
        self.content = content
        self.email_template = email_template
        self.receiver_user = receiver_user
        self.connection = connection
        self.email = None

    def create_mail(self):
        result = None
        tries = 0
        #while (result is None or result is not 1) and tries < 5:


        print("Sending new email to " + self.receiver_user.email)
        legal = LegalSetting.objects.first()
        self.context['content'] = self.content
        self.context['legal'] = legal
        html_content = render_to_string(self.email_template, context=self.context)
        print(self.content)

        email = EmailMultiAlternatives('Subject', self.subject, connection=self.connection)
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

        if 'files' in self.context and self.context['files']:
            for file_name, file in self.context['files'].items():
                email.attach(file_name, file, )

        if 'object' in self.context and isinstance(self.context['object'], OnlineShipment):
            email.attach_file(self.context['object'].file.path)

        if 'object' in self.context and isinstance(self.context['object'], Order):
            for order_item in self.context['object'].orderitem_set.all():
                if hasattr(order_item.product,'product') and order_item.product.product.product_picture():
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
        self.email = email

    def run(self):
        result =  self.email.send()
        print("Mail sent: "+ str(result))

class PaginatedFilterViews(View):
    def get_context_data(self, **kwargs):
        context = super(PaginatedFilterViews, self).get_context_data(**kwargs)
        if self.request.GET:
            querystring = self.request.GET.copy()
            if self.request.GET.get('page'):
                del querystring['page']
            context['querystring'] = querystring.urlencode()
        return context