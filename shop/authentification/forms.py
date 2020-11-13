from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, BooleanField
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from shop.models import Company, Contact


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
