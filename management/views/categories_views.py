from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic.edit import CreateView, UpdateView

from permissions.views.mixins import LoginRequiredMixin
from shop.models.products import ProductCategory


class CategoryCreationView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = 'categories'
    model = ProductCategory
    fields = '__all__'
    success_message = _("Category created successfully")

    def get_success_url(self):
        return reverse_lazy('category_edit_view', kwargs={'id': self.object.id})


class CategoryEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'management/generic/generic-edit.html'
    context_object_name = 'categories'
    model = ProductCategory
    fields = '__all__'

    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'id'
    success_message = _("Category updated successfully")

    def get_success_url(self):
        return reverse_lazy('category_edit_view', kwargs={'id': self.object.id})


class CategoryDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = ProductCategory
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Category deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('categories_overview')
