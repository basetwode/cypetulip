from django.shortcuts import render
# Create your views here.

from django.http import HttpResponse
from django.views.generic import View
from CMS.models import Page, Section, CSSSetting
from Permissions.error_handler import raise_404


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
        page = Page.objects.filter(page_name=site)
        all_pages = Page.objects.all()
        print('page 1' + page[0].link)
        print(page.count())
        if page.count() == 1:
            page = page[0]
            print(page.is_enabled)
            if page.is_enabled:
                print(page.link)
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
            red = int('0x'+main_color_lighter[:2], 16) + 6
            green = int('0x'+main_color_lighter[2:4], 16) + 6
            blue = int('0x'+main_color_lighter[4:6], 16) + 6
            main_color_lighter = ("0x%0.2X" % red )[2:4] + ("0x%0.2X" % green )[2:4] + ("0x%0.2X" % blue )[2:4]
            print(main_color_lighter)
            color_dict.setdefault('main_color', css_settings.main_color)
            color_dict.setdefault('main_color_lighter',main_color_lighter)
            color_dict.setdefault('second_color', css_settings.second_color)

        return render(request, self.template_name, color_dict,content_type='text/css')
