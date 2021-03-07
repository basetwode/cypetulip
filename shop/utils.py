import hashlib
import json
import logging
import re
import time

from django.http import HttpResponse

from shop.errors import FieldError, JsonResponse
from shop.models.orders import OrderItem, OrderDetail
from shop.models.products import Product

__author__ = 'Anselm'
logger = logging.getLogger(__name__)


def create_hash():
    gen_hash = hashlib.sha1()
    gen_hash.update(str(time.time()).encode('utf-8'))
    return gen_hash.hexdigest()[:-25]


def json_response(code, x):
    dump = json.dumps(x, sort_keys=True, indent=2)
    return HttpResponse(dump,
                        content_type='application/json; charset=UTF-8', status=code)


"""
    Checks if the required_arguments are given in the request POST parameters.
"""


def check_params(required_arguments, redirect_page=None, message=""):
    def real_decorator(func):
        def decorator(self, *args, **kwargs):
            request = args[0]

            missing_arguments = [FieldError(field_name=arg,
                                            message=message,
                                            mismatch=False if len(value) > 0 and arg not in request.POST
                                            else re.match(value, request.POST[arg]) is None)
                                 for
                                 arg, value in required_arguments.items() if arg not in request.POST
                                 or re.match(value, request.POST[arg]) is None
                                 ]

            list = JsonResponse(errors=missing_arguments, success=False)
            json_dump = list.dump()

            if len(missing_arguments) == 0:
                # All required args given
                return func(self, *args, **kwargs)

            logger.debug(
                "User request is missing following arguments or arguments could not be parsed %s" % json_dump)

            return json_response(code=400, x=list.dump())

        return decorator

    return real_decorator


def get_orderitems_once_only(order):
    order_items = OrderItem.objects.filter(order_detail=order, order_item__isnull=True).exclude(
        product__in=Product.objects.all())
    return order_items


def get_order_for_hash_and_contact(contact, uuid):
    company = contact[0].company
    order = OrderDetail.objects.filter(uuid=uuid, is_send=False, company=company)
    if order.count() > 0:
        order = order[0]
        return order
    return None
