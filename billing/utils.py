from functools import reduce

from django.db.models import Case, When, FloatField, F, Sum, Func, Transform, DecimalField
from django.db.models.functions import Cast


class Round(Func):
    function = 'ROUND'
    arity = 2
    arg_joiner = '::numeric, '

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sqlite(compiler, connection, arg_joiner=", ", **extra_context)


def calculate_sum(order_items, include_tax=False, include_discount=False):
    price_field = 'price'
    price_field_wt = 'price_wt'
    if include_discount:
        price_field = 'price_discounted'
        price_field_wt = 'price_discounted_wt'

    order_items = order_items.filter(allowable=True)
    if include_tax:
        total = order_items.aggregate(
            total=Round(Sum(price_field_wt, field=price_field_wt, output_field=DecimalField()), 2, output_field=DecimalField()))['total']
    else:
        total = order_items.aggregate(
            total=Round(Sum(price_field, field=price_field, output_field=DecimalField()), 2, output_field=DecimalField()))['total']
    return total if total else 0


def calculate_sum_order(order_items, include_tax=False, include_discount=False):
    price_field = 'total'
    price_field_wt = 'total_wt'
    if include_discount:
        price_field = 'total_discounted'
        price_field_wt = 'total_discounted_wt'
    order_items = order_items.filter(allowable=True)
    return reduce(lambda total, order_item: total + order_item,
                 [getattr(order_item, price_field_wt if include_tax else price_field)() for order_item in order_items \
                  .filter(order_item__isnull=True)],0)
