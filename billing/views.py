import os
from datetime import timedelta
from io import BytesIO

from django.db.models import FloatField, F
from django.db.models.functions import Cast
from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

from billing.utils import calculate_sum, Round
from home import settings
from management.models import LegalSetting
from payment.models import PaymentDetail
from shop.models import Order, OrderDetail, OrderItem


class HTMLPreview(View):
    def get(self, request, order):
        _order = Order.objects.get(order_hash=order)
        order_detail = OrderDetail.objects.get(order=_order)
        contact = order_detail.contact
        company = _order.company
        order_items = OrderItem.objects.filter(order=_order)

        legal_settings = LegalSetting.objects.first()

        template = get_template('invoice.html')
        context = {
            'order': _order,
            'order_items': order_items,
            'order_detail': order_detail,
            'contact': contact,
            'company': company,
            'invoice_settings': legal_settings
        }

        return render(request, 'invoice.html', context)


class GeneratePDF(View):
    def get(self, request, order):
        _order = Order.objects.get(order_hash=order)
        order_detail = OrderDetail.objects.get(order=_order)
        contact = order_detail.contact
        company = _order.company
        order_items = OrderItem.objects.filter(order=_order).annotate(
            price_t=Round(F('price') * Cast(F('count'), FloatField()),2),
        )
        order_detail.date_due = order_detail.date_bill + timedelta(days=company.term_of_payment)

        legal_settings = LegalSetting.objects.first()
        total_without_tax = calculate_sum(order_items)
        total_with_tax = calculate_sum(order_items, True)
        payment_detail = PaymentDetail.objects.get(order=_order)
        tax_rate = int(round(total_with_tax / total_without_tax, 2)*100)-100

        context = {
            'total': total_with_tax,
            'total_without_tax': total_without_tax,
            'tax': round(total_with_tax - total_without_tax, 2),
            'tax_rate': tax_rate,
            'order': _order,
            'order_detail': order_detail,
            'order_items': order_items,
            'contact': contact,
            'company': company,
            'payment_detail': payment_detail,
            'invoice_settings': legal_settings,
        }
        pdf = self.render_to_pdf('invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" % _order.order_hash
            content = "inline; filename='%s'" % filename
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % filename
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

    def render_to_pdf(self, template_src, context_dict=None):
        if context_dict is None:
            context_dict = {}
        template = get_template(template_src)
        html = template.render(context_dict)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=self.link_callback)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        return None

    def link_callback(self, uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        # use short variable names
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /static/media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri  # handle absolute uri (ie: http://some.tld/foo.png)

        # make sure that file exists
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path
