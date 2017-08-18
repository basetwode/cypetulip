import random
import secrets
import string

from django.core.files.storage import FileSystemStorage
from CAD_Shop import settings
import os
import time
import hashlib

__author__ = ''


fs = FileSystemStorage(location=settings.MEDIA_ROOT)


def company_files_upload_handler(company, filename):
    return "company/{company_hash}/{file}".format(company_hash=company.company_id, file=filename)


def order_files_upload_handler(order, filename):
    order.file_name = filename
    return "orders/{hash}/{file}".format(hash=order.order.order_hash, file=__create_hash(filename))


def public_files_upload_handler(instance, filename):
    return "public/{file}".format(file=__create_hash(filename))


def __create_hash(orig_filename):
    gen_hash = hashlib.sha1()
    gen_hash.update(str(time.time()))
    return gen_hash.hexdigest()[:-25] + os.path.splitext(orig_filename)[1]


def guid(*args):
    i = random.randrange(12, 25600)
    t = long(time.time() * 1000)
    r = long(random.random() * 100000000000000000L)
    a = random.random() * 100000000000000000L

    data = str(i) + ' ' + str(t) + ' ' + str(r) + ' ' + str(a) + ' ' + str(args)
    data = hashlib.md5(data).hexdigest()[10:]

    return data


def rand_key(size):
    return secrets.token_urlsafe(20)


