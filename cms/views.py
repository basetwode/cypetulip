from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, TemplateView, FormView

from cms.forms import ContactForm
from cms.models import CSSSetting, Page, Section
from management.models import MailSetting, LegalSetting
from permissions.error_handler import raise_404
# Create your views here.
from shop.models import Contact
from utils.mixins import EmailMixin


class AdminView(View):
    def get(self, request):
        # <view logic>
        return HttpResponse('CMSAdmin')

    def post(self, request):
        # <view logic>
        return HttpResponse('CMSAdmin')


# This is for added sites #
class GenericView(View):
    def get(self, request, site):
        page = Page.objects.filter(page_id=site)
        all_pages = Page.objects.all()
        if page.count() == 1:
            page = page[0]
            if page.is_enabled:
                if page.link:
                    sections = Section.objects.filter(page=page)
                    return render(request, 'index.html', {'page': page, 'sections': sections, 'all_pages': all_pages})
                else:
                    sections = Section.objects.filter(page=page)
                    return render(request, 'index.html', {'page': page, 'sections': sections, 'all_pages': all_pages})

        # <view logic>
        return raise_404(request)

    def post(self, request, site):
        # <view logic>
        return HttpResponse('GenericSite')


class CSSView(View):
    template_name = 'theme.css'

    def get(self, request):
        css_settings = CSSSetting.objects.all()
        color_dict = {}
        if css_settings.count() > 0:
            css_settings = css_settings[0]

            main_color_lighter = css_settings.main_color
            red = int('0x' + main_color_lighter[:2], 16) + 6
            green = int('0x' + main_color_lighter[2:4], 16) + 6
            blue = int('0x' + main_color_lighter[4:6], 16) + 6
            main_color_lighter = ("0x%0.2X" % red)[2:4] + ("0x%0.2X" % green)[2:4] + ("0x%0.2X" % blue)[2:4]
            print(main_color_lighter)
            color_dict.setdefault('main_color', css_settings.main_color)
            color_dict.setdefault('main_color_lighter', main_color_lighter)
            color_dict.setdefault('second_color', css_settings.second_color)

        return render(request, self.template_name, color_dict, content_type='text/css')


class PermissionDeniedView(TemplateView):
    template_name = 'permission_denied.html'


class ContactView(FormView, EmailMixin):
    template_name = 'contact.html'
    email_template = "mail/new_contact_request.html"
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


class GBTView(TemplateView):
    template_name = "predefined_page.html"

    def get_context_data(self, **kwargs):
        context = super(GBTView, self).get_context_data(**kwargs)
        legal = LegalSetting.objects.first()
        context['page_content'] = legal.general_business_term
        context['page_name'] = _("General Business Terms")
        return context


class LegalView(TemplateView):
    template_name = "legal.html"

    def get_context_data(self, **kwargs):
        context = super(LegalView, self).get_context_data(**kwargs)
        legal = LegalSetting.objects.first()
        context['legal'] = legal
        context['page_name'] = _("Legal")
        return context


class CancellationPolicyView(TemplateView):
    template_name = "predefined_page.html"

    def get_context_data(self, **kwargs):
        context = super(CancellationPolicyView, self).get_context_data(**kwargs)
        legal = LegalSetting.objects.first()
        context['page_content'] = legal.cancellation_policy
        context['page_name'] = _("Cancellation Policy")
        return context


class PrivacyPolicyView(TemplateView):
    template_name = "predefined_page.html"

    def get_context_data(self, **kwargs):
        context = super(PrivacyPolicyView, self).get_context_data(**kwargs)
        legal = LegalSetting.objects.first()
        context['page_content'] = legal.privacy_policy
        context['page_name'] = _("Privacy Policy")
        return context