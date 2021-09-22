import hashlib
import os
import random
import secrets
import time

from django.core.files.storage import FileSystemStorage

from home import settings

__author__ = ''


fs = FileSystemStorage(location=settings.MEDIA_ROOT)


def company_files_upload_handler(company, filename):
    return "company/{company_hash}/{file}".format(company_hash=company.company_id, file=filename)


def order_files_upload_handler(order, filename):
    order.file_name = filename
    return "orders/{hash}/order/{file}".format(hash=order.order_detail.uuid, file=__create_hash(filename))


def invoice_files_upload_handler(order, filename):
    return "orders/{hash}/invoice/Invoice_{file}.pdf".format(hash=order.uuid, file=order.unique_bill_nr())


def rma_files_upload_handler(rma, filename):
    return "orders/{hash}/rma/RMA_{file}.pdf".format(hash=rma.order.uuid, file=rma.number)


def shipment_files_upload_handler(shipment, filename):
    shipment.file_name = filename
    return "orders/{hash}/shipping/{file}".format(hash=shipment.order.uuid, file=__create_hash(filename))


def public_files_upload_handler(instance, filename):
    return "public/{file}".format(file=__create_hash(filename))


def __create_hash(orig_filename):
    gen_hash = hashlib.sha1()
    gen_hash.update(str(time.time()).encode('utf-8'))
    return gen_hash.hexdigest()[:-25] + os.path.splitext(orig_filename)[1]


def guid(*args):
    i = random.randrange(12, 25600)
    t = (time.time() * 1000)
    r = (random.random() * 100000000000000000)
    a = random.random() * 100000000000000000

    data = str(i) + ' ' + str(t) + ' ' + str(r) + ' ' + str(a) + ' ' + str(args)
    data = hashlib.md5(data).hexdigest()[10:]

    return data


def rand_key(size):
    return secrets.token_urlsafe(20)
