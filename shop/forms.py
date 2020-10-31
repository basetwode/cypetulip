from django.forms import CharField, ModelForm, Textarea
from django.utils.datastructures import MultiValueDictKeyError

from shop.models import ProductAttributeType, IndividualOffer


class ProductAttributeForm(ModelForm):
    class Meta:
        model = ProductAttributeType
        fields = []

    def __init__(self, product_attribute_types, *args, **kwargs):
        super().__init__(*args, **kwargs)
        interests = product_attribute_types  # kwargs.pop('product_attribute_types')
        request = args[0]
        for pa in product_attribute_types:
            field_name = '%s' % (pa.name,)
            self.fields[field_name] = CharField(required=False)
            try:
                self.initial[field_name] = request[pa.name]
            except (IndexError, MultiValueDictKeyError) as e:
                self.initial[field_name] = ''

    def clean(self):
        interests = set()
        i = 0
        field_name = '%s' % (i,)
        while self.cleaned_data.get(field_name):
            interest = self.cleaned_data[field_name]
            if interest in interests:
                self.add_error(field_name, 'Duplicate')
            else:
                interests.add(interest)
            i += 1
            field_name = 'interest_%s' % (i,)
        self.cleaned_data['interests'] = interests


class IndividualOfferForm(ModelForm):
    class Meta:
        model = IndividualOffer
        fields = '__all__'
        widgets = {
            'message': Textarea(attrs={'cols': 80, 'rows': 10}),
        }


