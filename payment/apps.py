from __future__ import unicode_literals

from django.apps import AppConfig
from paypalcheckoutsdk.core import SandboxEnvironment, PayPalHttpClient, LiveEnvironment

from home import settings


class PaymentConfig(AppConfig):
    name = 'payment'
    paypal_environment = None
    paypal_client = None

    def ready(self):
        from payment.models import PaymentProvider
        provider = PaymentProvider.objects.filter(api__contains="paypal")
        if provider.count() > 0:
            if provider[0].use_sandbox:
                self.paypal_environment = SandboxEnvironment(client_id=provider[0].user_name, client_secret=provider[0].secret)
            else:
                self.paypal_environment = LiveEnvironment(client_id=provider[0].user_name, client_secret=provider[0].secret)
            self.paypal_client = PayPalHttpClient(self.paypal_environment)