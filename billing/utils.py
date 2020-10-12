from django.db.models import Case, When, FloatField, F, Sum, Func, Transform
from django.db.models.functions import Cast


class Round(Func):
    function = 'ROUND'
    arity = 2


def calculate_sum(order_items, include_tax=False):
    total = (order_items.annotate(
        _price=Round(F('price') * ((F('product__tax') + 1)
                                   if include_tax else 1.0) * Cast(F('count'), FloatField()), 2)
    ).aggregate(
        total=Round(Sum('_price', field="_price"),2))['total']
    )
    return total
