from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.forms import ModelForm

from shop.models import Company, Contact


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')


class CompleteCompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'street', 'number', 'zipcode', 'city', 'term_of_payment']
        widgets = {'name': forms.HiddenInput(), 'term_of_payment': forms.HiddenInput()}

