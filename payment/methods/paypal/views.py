from django.http import HttpResponse
from django.shortcuts import render
from paypalrestsdk import Payment as PaypalPayment

from django.views.generic import View
__author__ = 'Anselm'


class PaypalPaymentView(View):

    #This methods shows a formular for entering paypal data
    def get(self, order_hash):
        pass

    #This one accepts the entered formular and creates a payment and then redirects to paypal
    def post(self, order_hash):
        pass


class PaypalPaymentConfirmationView(View):
    def get(self, order_hash, payment_hash):
        pass

    def post(self, order_hash, payment_hash):
        pass
