from __future__ import unicode_literals

from django.apps import AppConfig
from paypalcheckoutsdk.core import SandboxEnvironment, PayPalHttpClient, LiveEnvironment



class PaymentConfig(AppConfig):
    name = 'payment'
    paypal_environment = None
    paypal_client = None

    def ready(self):
        try:


            from payment.models import PaymentProvider
            from payment.models import PaymentMethod

            prepayment, created = PaymentProvider.objects.get_or_create(api="Prepayment")
            bill, created = PaymentProvider.objects.get_or_create(api="Bill")
            paypal, created = PaymentProvider.objects.get_or_create(api="PayPal")

            pp_method, created = PaymentMethod.objects.get_or_create(name="Prepayment", provider=prepayment)
            bill_method, created = PaymentMethod.objects.get_or_create(name="Bill", provider=bill)
            paypal_method, created = PaymentMethod.objects.get_or_create(name="PayPal", provider=paypal)

            provider = PaymentProvider.objects.filter(api__contains="paypal")
            if provider.count() > 0:
                if provider[0].use_sandbox:
                    self.paypal_environment = SandboxEnvironment(client_id=provider[0].user_name, client_secret=provider[0].secret)
                else:
                    self.paypal_environment = LiveEnvironment(client_id=provider[0].user_name, client_secret=provider[0].secret)
                self.paypal_client = PayPalHttpClient(self.paypal_environment)
        except:
            print("DB not migrated")