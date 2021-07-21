from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

__author__ = 'Anselm'

from cms.models.main import Page
from management.models.main import Header, Footer, CacheSetting
from payment.models.main import PaymentMethod
from shop.models.orders import OrderItem, OrderDetail
from shop.models.products import ProductCategory, Product
from shop.models.accounts import Contact


def get_open_orders(request):
    open_orders = {}
    if request.user.is_authenticated:
        contact = Contact.objects.filter(user_ptr=request.user)
        if contact.count() > 0:
            order = OrderDetail.objects.filter(company=contact[0].company, state__isnull=True)
            return collect_open_orders(order)
    elif request.session.session_key:
        order = OrderDetail.objects.filter(state__isnull=True, session=request.session.session_key)
        return collect_open_orders(order)
    else:
        request.session.save()
    return open_orders


def collect_open_orders(order):
    if order.count() > 0:
        items = OrderItem.objects.filter(order_detail=order[0], product__id__in=Product.objects.all())
        all_items = OrderItem.objects.filter(order_detail=order[0])
        sum = 0
        for item in all_items:
            sum += item.product.bprice_wt()
        total = 0
        number_items = 0
        for order in items:
            total += order.product.bprice_wt()
            number_items += 1
        return {'open_orders': items, 'total_cart': total, 'number_items': number_items, 'total_order': sum,
                }
    else:
        return {'open_orders': [], 'total_cart': 0, 'number_items': 0, 'total_order': 0}


def language(request):
    return {'language': 'de'}


def header(request):
    header = Header.objects.filter(is_enabled=True, language=request.LANGUAGE_CODE)
    if header:
        return {'header': header[0]}
    else:
        return {'footer': ''}


def footer(request):
    footer = Footer.objects.filter(is_enabled=True, language=request.LANGUAGE_CODE)
    if footer:
        pages = ''
        payment_methods = ''
        if footer[0].sitemap:
            pages = Page.objects.all()
        elif footer[0].payment_methods:
            payment_methods = PaymentMethod.objects.filter(enabled=True)
        return {'footer': footer[0], 'pages': pages, 'payment_methods': payment_methods}
    else:
        return {'footer': ''}


def categories(request):
    categories_list = ProductCategory.objects.all()
    return {'cms_categories': categories_list}


def cache_clear_neccessary(request):
    cache_settings = CacheSetting.objects.first()
    if cache_settings.cache_clear_required and request.user.is_superuser:
        messages.warning(request, _("Cache needs to be updated. Please go to cache management"))
    return {}
