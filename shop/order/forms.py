from django.forms import ModelForm
from requests.compat import basestring

from ..models import *

__author__ = 'Anselm'


class SubItemBaseForm(ModelForm):
    pass


class FileItemForm(SubItemBaseForm):
    class Meta:
        model = FileOrderItem
        fields = ['order', 'product', 'order_item', 'file']

    @staticmethod
    def _product_type():
        return "file"


class SelectItemForm(SubItemBaseForm):
    class Meta:
        model = SelectOrderItem
        fields = ['order', 'product', 'order_item', 'selected_item']

    @staticmethod
    def _product_type():
        return "selected_item"


class CheckboxItemForm(SubItemBaseForm):
    class Meta:
        model = CheckBoxOrderItem
        fields = ['order', 'product', 'order_item', 'is_checked']

    @staticmethod
    def _product_type():
        return "is_checked"


class NumberItemForm(SubItemBaseForm):
    class Meta:
        model = NumberOrderItem
        fields = ['order', 'product', 'order_item', 'number']

    @staticmethod
    def _product_type():
        return "number"


def SubItemForm(class_name, item, request):
    subclasses = SubItemBaseForm.__subclasses__()
    for subclass in subclasses:
        if subclass._product_type() == class_name:
            #instance = OrderItem.objects.filter(order_item__id=item.get('order_item'), product__id=item['product'])
            return subclass(item, {'file':item.get('file')}if item.get('file') else None)
                            #instance=instance[0] if instance.count() > 0 else None)


class ItemBuilder():
    import re
    item_string = '[{0}][{1}]{2}'
    pattern = re.compile(
        r'\[(?P<order_item_id>[0-9]*)\]\[(?P<order_id>[0-9]*)\]\[(?P<product_type>[\S]*)\](?P<product_id>[0-9]*)')

    def build(self, string, value):
        match = self.pattern.match(string)
        if match:
            order_id = match.group("order_id")
            order_item_id = match.group("order_item_id")
            product_type = match.group("product_type")
            product_id = match.group("product_id")
            order_id = int(order_id) if order_id else -1
            order_item_id = int(order_item_id) if order_item_id else -1
            product_id = int(product_id) if product_id else -1
            value = int(value) if isinstance(value, basestring) and value.isdigit() else value
            dict = {'order': order_id, '{}'.format(product_type): value, 'product_type': product_type,
                    'product': product_id, }
            if order_item_id >= 0:
                dict.setdefault('order_item', order_item_id)
            return dict
        return None

    def build_reverse(self, order_id, product_type, product_id):
        return self.item_string.format(order_id, product_type, product_id)
