from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView, DeleteView

from permissions.mixins import LoginRequiredMixin
from shop.models.products import IndividualOffer


class IndividualOfferRequestOverview(LoginRequiredMixin, ListView):
    template_name = 'management/offers/offers-individualoffers-overview.html'
    model = IndividualOffer
    paginate_by = 50
    ordering = ['-date_added']


class IndividualOfferRequestView(LoginRequiredMixin, DetailView):
    template_name = 'management/offers/offers-individualoffer.html'
    model = IndividualOffer
    context_object_name = 'offer'
    slug_url_kwarg = 'id'
    pk_url_kwarg = 'id'


class DeleteIndividualOfferRequest(LoginRequiredMixin, DeleteView):
    model = IndividualOffer
    success_url = reverse_lazy('individualoffers_overview')
    pk_url_kwarg = 'id'

    def get_success_url(self):
        messages.success(self.request, _('Individual offer request deleted'))
        return super().get_success_url()
