import os

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic import View, TemplateView, FormView

from cms.forms.forms import ContactForm, CSSSettingForm
from cms.models.main import Page, Section
from home.settings import STATIC_ROOT, CACHE_MIDDLEWARE_SECONDS
from management.models.main import MailSetting, LegalSetting, CacheSetting
from permissions.error_handler import raise_404
# Create your views here.
from permissions.views.mixins import LoginRequiredMixin
from shop.models.accounts import Contact
from utils.mixins import EmailMixin


class AdminView(View):
    def get(self, request):
        # <view logic>
        return HttpResponse('CMSAdmin')

    def post(self, request):
        # <view logic>
        return HttpResponse('CMSAdmin')


class CSSSettingsView(LoginRequiredMixin, FormView):
    form_class = CSSSettingForm
    template_name = 'cms/management/csssettings-edit.html'

    def get_context_data(self, **kwargs):
        context = super(CSSSettingsView, self).get_context_data(**kwargs)
        from django.contrib.staticfiles import finders
        result_f = finders.find('base.scss')
        template = open(result_f, 'r')
        form = {}
        for line in template.readlines():
            if line.startswith("$"):
                line = line.split(":")
                form.setdefault(line[0], line[1].replace(";\n", "").strip(" "))
        return {**context, **{'form': form}}

    def get_success_url(self):
        return reverse_lazy('css-settings', kwargs={'css_settings_id': 1})

    def form_valid(self, form):
        result = super(CSSSettingsView, self).form_valid(form)
        from django.contrib.staticfiles import finders
        result_f = finders.find('base.scss')
        template = open(result_f, 'r')

        new_template = ""
        for line in template.readlines():
            if line.startswith("$"):
                line = line.split(":")
                new_template += line[0] + ": " + form.data[line[0]] + ";\n"
            else:
                new_template += line
        template.close()
        out = open(result_f, 'w')
        out.writelines(new_template)
        out.close()
        with open(os.path.join(STATIC_ROOT, 'base.scss'), 'w') as out_static:
            out_static.writelines(new_template)
            out_static.close()
        cache_setting = CacheSetting.objects.first()
        cache_setting.cache_clear_required = True
        cache_setting.save()
        return result


# This is for added sites #
@method_decorator(vary_on_headers('User-Agent', 'Cookie'), name='dispatch')
@method_decorator(cache_page(CACHE_MIDDLEWARE_SECONDS), name='dispatch')
class GenericView(View):
    def get(self, request, site):
        page = Page.objects.filter(page_id=site)
        all_pages = Page.objects.all()
        if page.count() == 1:
            page = page[0]
            if page.is_enabled:
                sections = Section.objects.filter(page=page)
                return render(request, 'cms/index.html',
                              {'page': page, 'sections': sections, 'all_pages': all_pages})

        return raise_404(request)


class PermissionDeniedView(TemplateView):
    template_name = 'cms/permission_denied.html'


class ContactView(FormView, EmailMixin):
    template_name = 'cms/contact.html'
    email_template = "cms/mail/new_contact_request.html"
    form_class = ContactForm

    def form_valid(self, form):
        data = form.cleaned_data
        mail_setting = MailSetting.objects.first()
        contact = Contact()
        contact.email = mail_setting.contact_new_order

        self.send_mail(contact, _("New contact request"), "",
                       {'contact': contact,
                        'request_name': data['name'],
                        'request_email': data['email'],
                        'request_phone': data['phone'],
                        'request_message': data['message'],
                        })
        messages.success(self.request, _('Thank you for your request, we will contact you as soon as possible!'))
        return HttpResponseRedirect(reverse('contact'))


@method_decorator(vary_on_headers('User-Agent', 'Cookie'), name='dispatch')
@method_decorator(cache_page(CACHE_MIDDLEWARE_SECONDS), name='dispatch')
class GBTView(TemplateView):
    template_name = "cms/predefined_page.html"

    def get_context_data(self, **kwargs):
        context = super(GBTView, self).get_context_data(**kwargs)
        legal = LegalSetting.objects.first()
        context['page_content'] = legal.general_business_term
        context['page_name'] = _("General Business Terms")
        return context


@method_decorator(vary_on_headers('User-Agent', 'Cookie'), name='dispatch')
@method_decorator(cache_page(CACHE_MIDDLEWARE_SECONDS), name='dispatch')
class LegalView(TemplateView):
    template_name = "cms/legal.html"

    def get_context_data(self, **kwargs):
        context = super(LegalView, self).get_context_data(**kwargs)
        legal = LegalSetting.objects.first()
        context['legal'] = legal
        context['page_name'] = _("Legal")
        return context


@method_decorator(vary_on_headers('User-Agent', 'Cookie'), name='dispatch')
@method_decorator(cache_page(CACHE_MIDDLEWARE_SECONDS), name='dispatch')
class CancellationPolicyView(TemplateView):
    template_name = "cms/predefined_page.html"

    def get_context_data(self, **kwargs):
        context = super(CancellationPolicyView, self).get_context_data(**kwargs)
        legal = LegalSetting.objects.first()
        context['page_content'] = legal.cancellation_policy
        context['page_name'] = _("Cancellation Policy")
        return context

@method_decorator(vary_on_headers('User-Agent', 'Cookie'), name='dispatch')
@method_decorator(cache_page(CACHE_MIDDLEWARE_SECONDS), name='dispatch')
class PrivacyPolicyView(TemplateView):
    template_name = "cms/predefined_page.html"

    def get_context_data(self, **kwargs):
        context = super(PrivacyPolicyView, self).get_context_data(**kwargs)
        legal = LegalSetting.objects.first()
        context['page_content'] = legal.privacy_policy
        context['page_name'] = _("Privacy Policy")
        return context
