from django.db.models import Case, When, FloatField, F, Sum, Func, Transform
from django.db.models.functions import Cast


class Round(Func):
    function = 'ROUND'
    arity = 2


def calculate_sum(order_items, include_tax=False, include_discount=False):
    price_field = 'price'
    price_field_wt = 'price_wt'
    if include_discount:
        price_field = 'price_discounted'
        price_field_wt = 'price_discounted_wt'

    if include_tax:
        total = order_items.aggregate(
            total=Round(Sum(price_field_wt, field=price_field_wt), 2))['total']
    else:
        total = order_items.aggregate(
            total=Round(Sum(price_field, field=price_field), 2))['total']
    return total


