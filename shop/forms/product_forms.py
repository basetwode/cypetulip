from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.forms import CharField, ModelForm, Textarea, BooleanField
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from management.models.main import ShopSetting
from shop.models.products import ProductAttributeType, IndividualOffer


class ProductAttributeForm(ModelForm):
    class Meta:
        model = ProductAttributeType
        fields = []

    def __init__(self, product_attribute_types, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = args[0]
        for pa in product_attribute_types:
            field_name = '%s' % (pa.name,)
            self.fields[field_name] = CharField(required=False)
            try:
                self.initial[field_name] = '.'.join(request.getlist(pa.name))
            except (IndexError, MultiValueDictKeyError) as e:
                self.initial[field_name] = ''

    def clean(self):
        interests = set()
        i = 0
        field_name = '%s' % (i,)
        while self.cleaned_data.get(field_name):
            interest = self.cleaned_data[field_name]
            if interest in interests:
                self.add_error(field_name, 'Duplicate')
            else:
                interests.add(interest)
            i += 1
            field_name = 'interest_%s' % (i,)
        self.cleaned_data['interests'] = interests


class IndividualOfferForm(ModelForm):
    gdpr = BooleanField(required=True,
                        label=mark_safe(_("I hereby consent to the processing of my personal data. "
                                          "The information is only collected and processed for processing the contact request and "
                                          "is only stored for the period of communication, but for a maximum of 6 months. If a contract"
                                          " is concluded based on this request, legal retention periods apply. "
                                          "For more information, see our <a href='/cms/privacy-policy'>privacy policy</a>")))

    class Meta:
        model = IndividualOffer
        fields = '__all__'
        widgets = {
            'message': Textarea(attrs={'cols': 80, 'rows': 10}),
        }
        labels = {
            'gdpr': 'this is a label'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = ShopSetting.objects.first()

        self.fields['captcha'] = ReCaptchaField(widget=ReCaptchaV2Checkbox,
                                                public_key=settings.google_recaptcha_publickey,
                                                private_key=settings.google_recaptcha_privatekey)
