import threading
from email.mime.image import MIMEImage

from celery import shared_task
from django.apps import apps
from django.conf import settings as dsettings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.urls import resolve
from django.views import View
from django.views.generic.base import ContextMixin

from home import settings
from management.models.models import LegalSetting, MailSetting
from shipping.models.main import OnlineShipment
from shop.models.orders import OrderDetail


class EmailLogMixin:

    def log(self, **kwargs):
        pass
        # log = CommunicationLog(
        #     contact=
        #     kwargs
        # )

@shared_task
def send_mail_celery(receiver_user, content, subject, context, email_template):
    mail_thread = EmailThread(receiver_user, content, subject, context, email_template)
    mail_thread.create_mail()
    mail_thread.email.send()

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
            settings.EMAIL_PORT = mail_setting.smtp_port
            settings.DEFAULT_FROM_EMAIL = mail_setting.smtp_default_from
            # Optional SMTP authentication information for EMAIL_HOST.
            settings.EMAIL_HOST_USER = mail_setting.smtp_user
            settings.EMAIL_HOST_PASSWORD = mail_setting.smtp_password
            settings.EMAIL_USE_TLS = mail_setting.stmp_use_tls
        return get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
        )


    def send_mail(self, receiver_user, subject, content, context, email_to=None):
        print(dsettings.CELERY_BROKER_URL)

        # Serialize objects in context
        context.pop('form') if 'form' in context else None
        context.pop('view') if 'view' in context else None

        ObjectSerializer.deserialize(context)

        if dsettings.CELERY_BROKER_URL:
            send_mail_celery.delay(receiver_user.email, content, subject, context, self.get_template(), email_to)
        if not dsettings.CELERY_BROKER_URL:
            mail_thread = EmailThread(receiver_user.email, content, subject, context, self.get_template(), self.connection(), email_to)
            mail_thread.create_mail()
            mail_thread.start()


class EmailThread(threading.Thread):
    def __init__(self, receiver_user, content, subject, context, email_template, connection=None, email_to=None):
        super(EmailThread, self).__init__()
        self.subject = subject
        self.context = context
        self.content = content
        self.email_template = email_template
        self.receiver_user = receiver_user
        self.connection = connection or EmailMixin().connection()
        self.email = None
        self.email_to = email_to

    def create_mail(self):
        result = None
        tries = 0
        # while (result is None or result is not 1) and tries < 5:

        print("Sending new email to " + self.receiver_user)
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

        email.to = [self.receiver_user]
        if self.email_to:
            email.to.append(self.email_to)


        try:
            logo_file = legal.logo.open("rb")
            logo = MIMEImage(logo_file.read())
            logo.add_header('Content-ID', '<{}>'.format(legal.logo.name))
            email.attach(logo)
            logo_file.close()
        except:
            pass
        # Fill context with objects from database
        for k, v in self.context.items():
            if hasattr(v,'__len__') and 'type' in v:
                clazz = apps.get_model(app_label=v['app'], model_name=v['type'])
                try:
                    i = clazz.objects.get(id=v['id'])
                    self.context[k] = i
                except Exception as e:
                    print("Unable to serialize")


        if 'files' in self.context and self.context['files']:
            for file_name, file in self.context['files'].items():
                email.attach(file_name, open(file,'rb').read(), )

        if 'object' in self.context and isinstance(self.context['object'],OnlineShipment):
            email.attach_file(self.context['object'].file.path)

        if 'object' in self.context and isinstance(self.context['object'], OrderDetail):
            for order_item in self.context['object'].orderitem_set.filter(orderitem__isnull=True):
                if hasattr(order_item.product, 'product') and order_item.product.product.product_picture():

                    try:
                        product_file = order_item.product.product.product_picture().open("rb")
                        product_img = MIMEImage(product_file.read())
                        product_img.add_header('Content-ID', '<{}>'
                                               .format(order_item.product.product.product_picture().name))
                        email.attach(product_img)
                        product_file.close()
                    except:
                        pass

        print("from " + email.from_email)
        print("Sending mail")
        tries += 1
        self.email = email

    def run(self):
        result = self.email.send()
        print("Mail sent: " + str(result))


class PaginatedFilterViews(View):
    def get_context_data(self, **kwargs):
        context = super(PaginatedFilterViews, self).get_context_data(**kwargs)
        if self.request.GET:
            querystring = self.request.GET.copy()
            if self.request.GET.get('page'):
                del querystring['page']
            context['querystring'] = querystring.urlencode()
        return context


class APIMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super(APIMixin, self).get_context_data(**kwargs)
        context = {**context, **self.get_api_config()}
        return context

    def get_api_config(self):
        current_app = resolve(self.request.path)
        config = apps.get_app_config(current_app.app_name)
        return {'api_config': config.api[current_app.app_name]}


class ObjectSerializer():
    @staticmethod
    def deserialize(dictionary):
        for k, v in dictionary.items():
            if hasattr(v, '_meta'):
                serialized = {'type': v._meta.object_name, 'id': v.id,
                              'app': v._meta.app_label
                              }
                dictionary[k] = serialized
            if k == 'files' and v:
                for kfile, vfile in v.items():
                    dictionary['files'][kfile] = vfile.path
