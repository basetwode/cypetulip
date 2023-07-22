# Create your views here.
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView, DeleteView

from cms.views.mixins import GenericCreateView
from management.views.mixins import NotifyCustomerCreateView, NotifyCustomerUpdateView
from permissions.views.mixins import PermissionPostGetRequiredMixin
from shipping.forms.main import OnlineShipmentForm, PackageForm
from shipping.models.main import OnlineShipment, PackageShipment, Package, Shipment
from shop.models.orders import OrderState, OrderDetail


class CreateOnlineShipment(PermissionPostGetRequiredMixin, NotifyCustomerCreateView, GenericCreateView):
    model = OnlineShipment
    form_class = OnlineShipmentForm
    template_name = 'management/settings/settings-details.html'
    permission_get_required = ['shipping.view_onlineshipment']
    permission_post_required = ['shipping.add_onlineshipment']
    page_name = _("Ship order (Digital)")
    page_info = _("This will create a digital shipment, meaning that the customer "
                  "will be able to download the file directly from his account. "
                  "If the user ordered the file anonymously, it'll be send by mail")
    order_object = None

    def get_success_url(self):
        return reverse('management_order_detail_view', kwargs={'uuid': self.object.order.uuid})

    def form_valid(self, form):
        order: OrderDetail = self.get_order()
        self.order_object = order
        shipment: OnlineShipment = form.save(commit=False)
        shipment.order = order
        self.contact = self.get_order().contact
        order.state = OrderState.objects.get(is_sent_state=True)
        order.is_send = True
        order.save()
        messages.success(self.request, _("Shipment created"))
        return super().form_valid(form)

    def get_order(self):
        uuid = self.kwargs['order'] if 'order' in self.kwargs else None
        return get_object_or_404(OrderDetail, uuid=uuid)

    def get_form_kwargs(self):
        form_kwargs = super(CreateOnlineShipment, self).get_form_kwargs()
        return {**form_kwargs, **{'order_detail': self.get_order()}}


class CreatePackageShipment(PermissionPostGetRequiredMixin, NotifyCustomerCreateView, GenericCreateView):
    model = Package
    form_class = PackageForm
    permission_get_required = ['shipping.view_packagehipment']
    permission_post_required = ['shipping.add_packageshipment']
    template_name = 'management/settings/settings-details.html'
    page_name = _("Ship order")
    page_info = _("This will create a shipment and notify the customer that the item's been shipped")
    order_object = None

    def get_success_url(self):
        return reverse('management_order_detail_view', kwargs={'uuid': self.kwargs['order']})

    def form_valid(self, form):
        order: OrderDetail = self.get_order()
        self.order_object = order
        package = form.save(commit=True)
        package_shipment = PackageShipment(package=package)
        package_shipment.order = order
        package_shipment.save()
        package_shipment.order_items_shipped.clear()
        package_shipment.order_items_shipped.add(*form.cleaned_data['order_items_shipped'])
        package_shipment.save()
        self.contact = self.get_order().contact
        order.state = OrderState.objects.get(is_sent_state=True)
        order.save()
        messages.success(self.request, _("Shipment created"))
        return super().form_valid(form)

    def get_order(self):
        uuid = self.kwargs['order'] if 'order' in self.kwargs else None
        return get_object_or_404(OrderDetail, uuid=uuid)

    def get_form_kwargs(self):
        form_kwargs = super(CreatePackageShipment, self).get_form_kwargs()
        return {**form_kwargs, **{'order_detail': self.get_order()}}


class ShowOnlineShipment(PermissionPostGetRequiredMixin, NotifyCustomerUpdateView, UpdateView):
    model = OnlineShipment
    template_name = 'management/settings/settings-details.html'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    fields = ['file']
    permission_get_required = ['shipping.view_onlineshipment']
    permission_post_required = ['shipping.edit_onlineshipment']
    page_name = _("Shipment (Digital)")
    page_info = _("Update digital shipment")

    def get_context_data(self, **kwargs):
        return {**{"page_name": f"{self.page_name} - "
                                f"{self.object.order.unique_nr()}", "page_info": self.page_info},
                **super().get_context_data()}

    def get_success_url(self):
        return reverse('management_order_detail_view', kwargs={'order': self.object.order.uuid})

    def form_valid(self, form):
        self.contact = self.object.order.contact
        self.order_object = self.object.order
        return super().form_valid(form)


class ShowPackageShipment(PermissionPostGetRequiredMixin, UpdateView):
    model = Package
    template_name = 'management/settings/settings-details.html'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    fields = '__all__'
    permission_get_required = ['shipping.view_packageshipment']
    permission_post_required = ['shipping.edit_packageshipment']
    page_name = _("Shipment")
    page_info = _("Update shipment")

    def get_success_url(self):
        return reverse('management_order_detail_view', kwargs={'order': self.get_order().uuid})

    def get_context_data(self, **kwargs):
        return {**{"page_name": f"{self.page_name} - "
                                f"{self.get_order().unique_nr()}", "page_info": self.page_info},
                **super().get_context_data()}

    def get_order(self):
        return get_object_or_404(PackageShipment, package=self.object).order

    def form_valid(self, form):
        self.contact = self.get_order().contact
        self.order_object = self.get_order()
        return super().form_valid(form)


class DeleteShipment(PermissionPostGetRequiredMixin, DeleteView):
    model = Shipment
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''

    def get_success_url(self):
        return reverse('management_order_detail_view', kwargs={'order': self.kwargs['order']})
