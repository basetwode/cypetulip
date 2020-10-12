from django.db.models import When, FloatField, Case, Count, F
from django.db.models.functions import Round
from django.views import View


class TaxView(View):

    def add_tax_to_product(self, products):
        products.annotate(tprice=Round((Case(
            When(special_price=False, then='price'),
            When(special_price__gte=0, then='special_price'),
            default='price',
            output_field=FloatField(),
        ) * (F('tax') + 1), FloatField(), 2)))