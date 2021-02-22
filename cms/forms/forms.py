from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.forms import BooleanField, CharField, EmailField
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from management.models.models import ShopSetting


class ContactForm(forms.Form):
    name = CharField()
    email = EmailField()
    phone = CharField()
    message = CharField(widget=forms.Textarea)
    gdpr = BooleanField(required=True,
                        label=mark_safe(_("I hereby consent to the processing of my personal data. "
                                          "The information is only collected and processed for processing the contact request and "
                                          "is only stored for the period of communication, but for a maximum of 6 months. If a contract"
                                          " is concluded based on this request, legal retention periods apply. "
                                          "For more information, see our <a href='/cms/privacy-policy'>privacy policy</a>")))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = ShopSetting.objects.first()

        self.fields['captcha'] = ReCaptchaField(widget=ReCaptchaV2Checkbox,
                                                public_key=settings.google_recaptcha_publickey,
                                                private_key=settings.google_recaptcha_privatekey)


class CSSSettingForm(forms.Form):
    pass
