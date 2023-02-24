from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django_filters.views import FilterView

from permissions.views.mixins import LoginRequiredMixin
from shop.models.orders import Discount, FixedAmountDiscount, PercentageDiscount
from utils.mixins import PaginatedFilterViews
from utils.views import CreateUpdateView


class PercentageDiscountEditView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'management/generic/generic-edit.html'
    model = PercentageDiscount
    fields = '__all__'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    success_message = _("Discount updated successfully")

    def get_success_url(self):
        return reverse_lazy('percentage_discount_edit_view', kwargs={'id': self.object.id})


class FixedAmountDiscountEditView(SuccessMessageMixin, LoginRequiredMixin, CreateUpdateView):
    template_name = 'management/generic/generic-edit.html'
    model = FixedAmountDiscount
    fields = '__all__'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    success_message = _("Discount updated successfully")

    def get_success_url(self):
        return reverse_lazy('fixed_discount_edit_view', kwargs={'id': self.object.id})


class DiscountOverview(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'management/discounts/discounts-overview.html'
    model = Discount
    paginate_by = 50
    ordering = ['-date_added']
