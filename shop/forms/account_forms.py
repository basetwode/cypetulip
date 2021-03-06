from django.forms import ModelForm

from shop.models.accounts import Company, Contact


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ('username', 'gender', 'title', 'first_name', 'last_name')
        labels = {
            'username': 'E-Mail'
        }



class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
        exclude = ['company_id', 'term_of_payment', ]


class PasswordResetView:
    class Meta:
        model = Contact
        fields = ['old_password', 'new_password1',
                  'new_password2']
