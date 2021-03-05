from django.forms import ModelForm, ModelMultipleChoiceField
from django.utils.translation import ugettext_lazy as _

from shipping.models import Shipment, OnlineShipment, PackageShipment, Package
from shop.models.orders import OrderItem


class OnlineShipmentForm(ModelForm):
    class Meta:
        model = OnlineShipment

        fields = ('file','order_items_shipped' )
        localized_fields = '__all__'

        labels = {
            'file': _('File'), 'order_items_shipped': _('Shipped Items')
        }

    def __init__(self, order_detail, *args, **kwargs):
        super(OnlineShipmentForm, self).__init__(*args, **kwargs)
        self.fields['order_items_shipped'].queryset = OrderItem.objects.filter(order_detail=order_detail, shipment__isnull=True, order_item__isnull=True)


class PackageForm(ModelForm):
    order_items_shipped = ModelMultipleChoiceField(queryset=OrderItem.objects.all())

    class Meta:
        model = Package
        fields = ['name', 'price', 'weight', 'tracking_code', 'shipper', 'order_items_shipped']
        localized_fields = '__all__'

        labels = {
            'name': _('Name'), 'price': _('Price'), 'weight': _('Weight'), 'tracking_code': _('Tracking code'),
            'shipper': _('Shipper'), 'order_items_shipped': _('Shipped Items')
        }

    def __init__(self, order_detail, *args, **kwargs):
        super(PackageForm, self).__init__(*args, **kwargs)
        self.fields['order_items_shipped'].queryset = OrderItem.objects.filter(order_detail=order_detail, shipment__isnull=True, order_item__isnull=True)