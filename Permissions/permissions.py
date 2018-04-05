import re
from functools import wraps

from django.contrib.auth.models import User
from django.shortcuts import redirect

from Permissions.error_handler import raise_401
# from models import App, AppPermissions
from Permissions.models import AppUrl, AppUrlPermission
from Permissions.utils import show_urls
from Shop.models import Order, OrderDetail, Contact, Company

__author__ = 'Anselm'


# Todo: add another method that checks if an user has permissions on an order depending on if he's an employee of the company which the order belongs to.


# Checks if a user has access to a specific app
# Is used as annotation for other functions
def __has_access(user, app):
    if user and app:
        # app = App.objects.get(app_name=app)
        # app_permission = AppPermissions.objects.filter(app=app, user=user)
        # if app_permission.count() > 0 and app_permission[0].access:
        return True
    if user.is_superuser:
        return True
    return False


def __check_company_access(user, company_id):
    if user.is_superuser:
        return True
    company = Company.objects.filter(company_id=company_id)
    if company:
        user_filtered = Contact.objects.filter(company=company,user=user.id)
        if user_filtered:
            return True
    return False


def __check_order_access(user, order_id):
    #if user.is_superuser:
      #  return True
    contact = Contact.objects.filter(user=user.id)
    company = contact[0].company
    _order = Order.objects.filter(order_hash=order_id, company=company)
    if _order.count() > 0:

        return True
    return False


# Extracts the requested app from the URL
def __get_app_from_url(request):
    url = request[1:]
    url = url[:url.find('/')]
    return url


def __get_string_from_url(request,string_to_find):
    url = request[1:]
    url = url[url.find(string_to_find):]
    url = url[url.find('/') + 1:]
    url = url[:url.find('/')]
    return url


def check_serve_perms2(func):
    def decorator(self, *args, **kwargs):
        request = args[0]

        if 'order' in kwargs:
            order = kwargs.get('order')
            order_access = __check_order_access(request.user, order)
            print(order)
        elif 'company' in request.path:
            company = __get_string_from_url(request.path,'company')
            order_access = __check_company_access(request.user, company)
        else:
            order_access = True

        if request.user.is_authenticated() and \
                __has_access(request.user,
                             __get_app_from_url(request.path)) \
                and order_access:

            # User is allowed
            return func(self, *args, **kwargs)

        # User is not allowed
        return raise_401(request)

    return decorator

def check_serve_perms(func):
    def decorator(self, *args, **kwargs):
        request = args[0]
        method = request.method
        url = request.path
        app = __get_app_from_url(url)
        urls = AppUrl.objects.filter(app__name=app)
        access = False
        app_url = [app_url for app_url in urls if re.compile(app_url.url).match(url)]
        message = None
        if len(app_url)==1:
            app_url=app_url[0]
            app_url_permission = AppUrlPermission.objects.filter(url=app_url,user=request.user)
            if len(app_url_permission)==1:
                app_url_permission = app_url_permission[0]
                if method == 'POST':
                    message = app_url_permission.post_message
                    access = app_url_permission.post_access
                elif method =='GET':
                    message = app_url_permission.get_message
                    access = app_url_permission.get_access
        if request.user.is_authenticated and request.user.is_staff:
            access = True
        elif 'order' in kwargs and access:
            order = kwargs.get('order')
            access = __check_order_access(request.user, order)
            print(order)
        elif 'company' in request.path and access:
            company = __get_string_from_url(request.path, 'company')
            access = __check_company_access(request.user, company)

        if access:
            return func(self, *args, **kwargs)
        else:
            return raise_401(request,{'message':message})

    return decorator

