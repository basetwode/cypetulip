from django_filters.views import FilterView

from permissions.mixins import LoginRequiredMixin
from shipping.models import Shipment
from shop.filters import ShipmentFilter
from utils.mixins import PaginatedFilterViews


class ShipmentOverview(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'management/shipments/shipments-overview.html'
    context_object_name = 'shipment'
    model = Shipment
    filterset_class = ShipmentFilter
