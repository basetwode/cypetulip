from django.db.models import Case, When, FloatField, F, Sum, Func, Transform
from django.db.models.functions import Cast


class Round(Func):
    function = 'ROUND'
    arity = 2


def calculate_sum(order_items, include_tax=False):
    if include_tax:
        total = order_items.aggregate(
            total=Round(Sum('price_wt', field="price"), 2))['total']
    else:
        total = order_items.aggregate(
            total=Round(Sum('price', field="price"), 2))['total']
    return total
