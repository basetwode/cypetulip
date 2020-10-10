from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

__author__ = 'Anselm'



class SofortPayment(View):
    template_name = 'product-detail.html'

    def get(self, request, product):

        return render(request, self.template_name, {'product': selected_product,
                                                    'categories': categories})

    def post(self, request):
        # <view logic>
        return HttpResponse('result')

    # This step ist the first which initiates the payment
    # and sends the data to sofortueberweisung
    def step1(self):
        pass
