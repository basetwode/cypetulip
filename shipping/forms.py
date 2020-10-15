from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from shipping.models import Shipment, OnlineShipment, PackageShipment, Package




class OnlineShipmentForm(ModelForm):
    class Meta:
        model = OnlineShipment

        fields = ('file', )
        localized_fields = '__all__'

        labels = {
            'file': _('File')
        }


class PackageForm(ModelForm):
    class Meta:
        model = Package
        fields = '__all__'
        localized_fields = '__all__'

        labels = {
            'name': _('Name'), 'price': _('Price'), 'weight': _('Weight'), 'Tracking code': _('tracking_code'),
            'shipper': _('Shipper')
        }

