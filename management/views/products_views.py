from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView

from management.forms.forms import ProductForm
from permissions.mixins import LoginRequiredMixin
from shop.filters.filters import ProductFilter, ProductSubItemFilter
from shop.views.mixins import WizardView, RepeatableWizardView
from shop.models import Product, FileSubItem, ProductSubItem, NumberSubItem, CheckBoxSubItem, SelectSubItem, SelectItem
from utils.mixins import PaginatedFilterViews
from utils.views import CreateUpdateView


class ProductsOverview(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'management/products/products-overview.html'
    context_object_name = 'products'
    model = Product
    paginate_by = 40
    ordering = 'id'
    filterset_class = ProductFilter


class SubItemOverview(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'management/products/subitems-overview.html'
    context_object_name = 'filesubitem'
    paginate_by = 40
    model = ProductSubItem
    filterset_class = ProductSubItemFilter

    def get_queryset(self):
        return super(SubItemOverview, self).get_queryset().filter(product=None)


class ProductCreationView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'management/products/product-create-vue.html'
    context_object_name = 'products'
    model = Product
    form_class = ProductForm
    success_message = _("Product created successfully")

    def get_success_url(self):
        return reverse_lazy('product_edit_view', kwargs={'product_id': self.object.id})


class ProductEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = 'management/products/product-create-vue.html'
    context_object_name = 'products'
    form_class = ProductForm
    model = Product
    product_id = None
    slug_field = 'id'
    slug_url_kwarg = 'product_id'
    success_message = _("Product updated successfully")

    def get_success_url(self):
        return reverse_lazy('product_edit_view', kwargs={'product_id': self.object.id})


class ProductDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Product
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Product deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('products_overview')


class CheckboxSubItemCreateUpdateView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = CheckBoxSubItem
    fields = ['price', 'tax', 'price_on_request', 'name', 'description', 'details',
              'is_required', 'is_multiple_per_item', 'is_once_per_order'
              ]
    success_message = _("Subitem updated successfully")

    def get_success_url(self):
        return reverse_lazy('checkboxsubitem_create_view', kwargs={'id': self.object.id})


class NumberSubItemCreateUpdateView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = NumberSubItem
    fields = ['price', 'tax', 'price_on_request', 'name', 'description', 'details',
              'is_required', 'is_multiple_per_item', 'is_once_per_order'
              ]
    success_message = _("Subitem updated successfully")

    def get_success_url(self):
        return reverse_lazy('idnumbersubitem_create_view', kwargs={'id': self.object.id})


class FileSubItemCreationView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = FileSubItem
    fields = ['price', 'tax', 'price_on_request', 'name', 'description', 'details',
              'is_required', 'is_multiple_per_item', 'is_once_per_order',
              'extensions']
    success_message = _("Subitem updated successfully")

    def get_success_url(self):
        return reverse_lazy('filesubitem_create', kwargs={'id': self.object.id})


class SelectSubItemCreationView(SuccessMessageMixin, LoginRequiredMixin, WizardView):
    page_title = _('Create Selectsubitem')
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = SelectSubItem
    fields = ['price', 'tax', 'price_on_request', 'name', 'description', 'details',
              'is_required', 'is_multiple_per_item', 'is_once_per_order',
              ]
    success_message = _("Subitem updated successfully")

    def get_success_url(self):
        return reverse_lazy('selectsubitem_create_view', kwargs={'id': self.object.id})


class SelectItemCreationView(SuccessMessageMixin, LoginRequiredMixin, RepeatableWizardView):
    page_title = _('Create new select item')
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = SelectItem
    fields = ['name', 'price', 'tax']
    pk_url_kwarg = 'id'
    parent_key = 'select'
    self_url = 'selectitem_create_view'
    delete_url = 'selectitem_delete'
    success_message = _("Selectitem updated successfully")

    def get_back_url(self):
        return reverse_lazy('selectsubitem_create_view', kwargs={'id': self.get_parent_id()})

    def get_next_url(self):
        return reverse_lazy('subitem_overview')

    def get_success_url(self):
        return reverse_lazy('selectitem_create_view', kwargs={'id': '', 'parent_id': self.get_parent_id()})

    def form_valid(self, form):
        selectitem = form.save(commit=False)
        selectitem.select = SelectSubItem.objects.get(id=self.get_parent_id())
        return super(SelectItemCreationView, self).form_valid(form)


class SelectItemDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = SelectItem
    slug_field = 'id'
    pk_url_kwarg = 'id'
    template = ''
    success_message = _("Select Item deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('subitem_overview')


class SubItemDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = ProductSubItem
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Subitem deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('subitem_overview')
