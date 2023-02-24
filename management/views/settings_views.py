from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core import management
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView

from management.forms.forms import PaymentProviderForm, ClearCacheForm
from management.models.main import LdapSetting, MailSetting, LegalSetting, ShopSetting, CacheSetting
from payment.models.main import PaymentMethod, PaymentProvider
from permissions.views.mixins import LoginRequiredMixin
from utils.views import CreateUpdateView


class MailSettingsDetailView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'management/settings/settings-details.html'
    id = None
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = MailSetting
    fields = '__all__'
    success_message = _("Mailsettings updated successfully")

    def get_success_url(self):
        return reverse_lazy('mail_settings_details', kwargs={'id': self.object.id})


class ShopSettingsDetailView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'management/settings/settings-details.html'
    id = None
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = ShopSetting
    fields = '__all__'
    success_message = _("Shopsettings updated successfully")

    def get_success_url(self):
        return reverse_lazy('shop_settings_details', kwargs={'id': self.object.id})


class LdapSettingsDetailView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'management/settings/settings-details.html'
    id = None
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = LdapSetting
    fields = '__all__'
    success_message = _("Ldapsettings updated successfully")

    def get_success_url(self):
        return reverse_lazy('ldap_settings_details', kwargs={'id': self.object.id})


class LegalSettingsDetailView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'management/settings/settings-details.html'
    id = None
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = LegalSetting
    fields = '__all__'
    success_message = _("Ldapsettings updated successfully")

    def get_success_url(self):
        return reverse_lazy('legal_settings_details', kwargs={'id': self.object.id})


class CacheManagementView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = 'management/settings/settings-cache.html'
    form_class = ClearCacheForm
    success_url = reverse_lazy('cache_settings_details')

    def form_valid(self, form):
        form_valid = super(CacheManagementView, self).form_valid(form)
        if form.cleaned_data['clear_html_cache']:
            self.flush_cache()
            messages.success(self.request, _("HTML Cache cleared successfully"))
        if form.cleaned_data['recompile_css_js']:
            try:
                management.call_command('collectstatic', verbosity=0, interactive=False)
                management.call_command('compress', verbosity=0)
                messages.success(self.request, _("JS/CSS successfully recompiled"))
            except:
                messages.error(self.request, _("Offline compression not enabled. CSS/JS are generated on-the-fly"))

            cache_setting = CacheSetting.objects.first()
            cache_setting.cache_clear_required = False
            cache_setting.save()
        return form_valid

    def flush_cache(self):
        from django.core.cache import cache
        cache.clear()


class PaymentProviderSettings(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = 'management/settings/settings-payment.html'
    form_class = PaymentProviderForm
    success_url = reverse_lazy('payment_settings_details')
    success_message = _("Payment settings saved!")

    def form_valid(self, form):
        paypal_provider = PaymentProvider.objects.get(api="PayPal")
        paypal_method = PaymentMethod.objects.get(provider=paypal_provider)
        invoice_provider = PaymentProvider.objects.get(api="Bill")
        invoice_method = PaymentMethod.objects.get(provider=invoice_provider)
        prepayment_provider = PaymentProvider.objects.get(api="Prepayment")
        prepayment_method = PaymentMethod.objects.get(provider=prepayment_provider)

        invoice_method.enabled = form.cleaned_data['invoice_enabled']
        invoice_method.details = form.cleaned_data['prepayment_description']
        prepayment_method.enabled = form.cleaned_data['prepayment_enabled']
        prepayment_method.details = form.cleaned_data['invoice_description']
        paypal_method.enabled = form.cleaned_data['paypal_enabled']
        paypal_method.details = form.cleaned_data['paypal_description']
        paypal_provider.user_name = form.cleaned_data['paypal_user']
        paypal_provider.secret = form.cleaned_data['paypal_secret']
        paypal_provider.use_sandbox = form.cleaned_data['paypal_use_sandbox']

        invoice_method.save()
        prepayment_method.save()
        paypal_method.save()
        paypal_provider.save()
        return super(PaymentProviderSettings, self).form_valid(form)

    def get_initial(self):
        initial = super(PaymentProviderSettings, self).get_initial()
        paypal_provider, created = PaymentProvider.objects.get_or_create(api="PayPal")
        paypal_method, created = PaymentMethod.objects.get_or_create(provider=paypal_provider, name="PayPal")
        invoice_provider, created = PaymentProvider.objects.get_or_create(api="Bill")
        invoice_method, created = PaymentMethod.objects.get_or_create(provider=invoice_provider, name="Bill")
        prepayment_provider, created = PaymentProvider.objects.get_or_create(api="Prepayment")
        prepayment_method, created = PaymentMethod.objects.get_or_create(provider=prepayment_provider,
                                                                         name="Prepayment")
        initial.update({'prepayment_enabled': prepayment_method.enabled,
                        'prepayment_description': prepayment_method.details,
                        'invoice_enabled': invoice_method.enabled,
                        'invoice_description': invoice_method.details,
                        'paypal_enabled': paypal_method.enabled,
                        'paypal_description': paypal_method.details,
                        'paypal_user': paypal_provider.user_name,
                        'paypal_secret': paypal_provider.secret,
                        'paypal_use_sandbox': paypal_provider.use_sandbox,
                        })
        return initial
