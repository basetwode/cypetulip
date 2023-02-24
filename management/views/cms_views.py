from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView

from cms.models.main import Page, Section
from management.models.main import Header, Footer
from permissions.views.mixins import LoginRequiredMixin
from shop.filters.filters import ProductCategoryFilter, SectionFilter, \
    PageFilter, FooterFilter, HeaderFilter
from shop.models.products import ProductCategory
from utils.mixins import PaginatedFilterViews


class CategoriesOverview(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'management/categories/categories-overview.html'
    context_object_name = 'categories'
    model = ProductCategory
    filterset_class = ProductCategoryFilter


class PagesOverview(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'management/cms/cms-pages-overview.html'
    context_object_name = 'pages'
    model = Page
    filterset_class = PageFilter


class PageCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = 'page'
    model = Page
    fields = '__all__'
    success_message = _("Page created successfully")

    def get_success_url(self):
        return reverse_lazy('page_edit_view', kwargs={'page_id': self.object.id})


class PageEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'management/generic/generic-edit.html'
    context_object_name = 'pages'
    model = Page
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'page_id'
    success_message = _("Page updated successfully")

    def get_success_url(self):
        return reverse_lazy('page_edit_view', kwargs={'page_id': self.object.id})


class PageDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Page
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Page deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('pages_overview')


class SectionsOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'management/cms/cms-sections-overview.html'
    context_object_name = 'sections'
    model = Section
    filterset_class = SectionFilter


class SectionCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = 'sections'
    model = Section
    fields = '__all__'
    success_message = _("Section created successfully")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['sections'] = Section.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy('section_edit_view', kwargs={'id': self.object.id})


class SectionEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'management/generic/generic-edit.html'
    context_object_name = 'sections'
    model = Section
    fields = '__all__'
    success_message = _("Section updated successfully")

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_success_url(self):
        return reverse_lazy('section_edit_view', kwargs={'id': self.object.id})


class SectionDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Section
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Section deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('sections')


class HeadersOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'management/cms/cms-headers-overview.html'
    context_object_name = 'headers'
    model = Header
    filterset_class = HeaderFilter


class HeaderCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = 'header'
    model = Header
    fields = '__all__'
    success_message = _("Header created successfully")

    def get_success_url(self):
        return reverse_lazy('header_edit', kwargs={'id': self.object.id})


class HeaderEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'management/generic/generic-edit.html'
    context_object_name = 'header'
    model = Header
    fields = '__all__'

    slug_field = 'id'
    slug_url_kwarg = 'id'
    success_message = _("Header updated successfully")

    def get_success_url(self):
        return reverse_lazy('header_edit', kwargs={'id': self.object.id})


class HeaderDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Header
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Header deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('headers_overview')


class FootersOverviewView(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'management/cms/cms-footers-overview.html'
    context_object_name = 'footers'
    model = Footer
    filterset_class = FooterFilter


class FooterCreateView(LoginRequiredMixin, CreateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = 'footer'
    model = Footer
    fields = '__all__'
    success_message = _("Footer created successfully")

    def get_success_url(self):
        return reverse_lazy('footer_edit', kwargs={'id': self.object.id})


class FooterEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'management/generic/generic-edit.html'
    context_object_name = 'footer'
    model = Footer
    fields = '__all__'

    slug_field = 'id'
    slug_url_kwarg = 'id'
    success_message = _("Footer updated successfully")

    def get_success_url(self):
        return reverse_lazy('footer_edit', kwargs={'id': self.object.id})


class FooterDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Footer
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Footer deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('footers_overview')
