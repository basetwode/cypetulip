import hashlib
import json
import logging
import re
import time
from abc import ABCMeta, abstractmethod

from django.http import HttpResponse

from Permissions.error_handler import raise_401
from Shop.Errors import FieldError, JsonResponse

__author__ = 'Anselm'
logger = logging.getLogger(__name__)




def create_hash():
    gen_hash = hashlib.sha1()
    gen_hash.update(str(time.time()))
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


