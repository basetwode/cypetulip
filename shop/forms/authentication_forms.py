from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.mail import EmailMultiAlternatives, get_connection
from django.forms import ModelForm, BooleanField
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from home import settings
from management.models.models import MailSetting
from shop.models.accounts import Company, Contact


class SignUpForm(UserCreationForm):
    gdpr = BooleanField(required=True,
                        label=mark_safe(_("I hereby consent to the processing of my personal data. "
                                "The information is only collected and processed for the purpose of registration "
                                "The basis is Art. 6 Para. 1 lit. b GDPR. The storage period is until the customer "
                                "manually deletes the account. For more information, see our <a href='/cms/privacy-policy'>privacy policy</a>")))

    class Meta:
        model = Contact
        fields = ('username', 'gender','title', 'first_name', 'last_name', 'password1', 'password2', )
        labels = {
            'username': 'E-Mail'
        }

class CompleteCompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'street', 'number', 'zipcode', 'city', 'term_of_payment']
        widgets = {'name': forms.HiddenInput(), 'term_of_payment': forms.HiddenInput()}



class PasswordResetFormSMTP(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

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

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email], connection=self.connection())
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')
        email_message.send()
