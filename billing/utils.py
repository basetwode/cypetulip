from django.db.models import Case, When, FloatField, F, Sum, Func, Transform
from django.db.models.functions import Cast


class Round(Func):
    function = 'ROUND'
    arity = 2
    # Only works as the arity is 2
    arg_joiner = '::numeric, '

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sqlite(compiler, connection, arg_joiner=", ", **extra_context)


def calculate_sum(order_items, include_tax=False):
    total = (order_items.annotate(
        _price=Round(F('price') * ((F('product__tax') + 1)
                                   if include_tax else 1.0) * Cast(F('count'), FloatField()), 2)
    #
    #             total = (order_items.annotate(
    #             _price=Round((Case(
    #             When(product__special_price=False, then='product__price'),
    #         When(product__special_price__gte=0, then='product__special_price'),
    #         default='product__price',
    #                 output_field=FloatField(),
    # ) * ((F('product__tax') + 1) if include_tax else 1.0) * Cast(F('count'), FloatField())), 2)
    ).aggregate(
        total=Round(Sum('_price', field="_price"),2))['total']
    )
    return total
