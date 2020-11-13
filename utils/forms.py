from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, PasswordInput
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class SearchField(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs)
        inline_code = mark_safe(
            "<script>"
            '$("#id_search").on("keyup", function() {'
            'var value = $(this).val().toLowerCase();'
            '$(".searchable *").filter(function() {'
            '$(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)'
            '});'
            '});'
            "</script>"
        )
        return html + inline_code


class SearchableSelect(forms.Select):
    def render(self, name, value, attrs=None, renderer=None):
        attrs.pop('multiple', None)
        attrs.update({'class': 'searchable form-control'})
        attrs.update({'size': 10})
        return super(SearchableSelect, self).render(name, value, attrs, renderer)


class SetPasswordForm(ModelForm):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = CharField(
        label=_("New password"),
        widget=PasswordInput(render_value=True),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=PasswordInput(render_value=True),

    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.instance)
        return password2

    def save(self, commit=True):
        instance = super(SetPasswordForm, self).save(commit=False)
        password = self.cleaned_data["new_password1"]
        instance.set_password(password)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = User
        fields = []
        labels = {
            'new_password1': _('New password'),
            'new_password2': _('Repeat password')
        }

