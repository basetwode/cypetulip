__author__ = ''


class PaypalResource:
    def __init__(self, intent, payer, transactions, redirect_urls):
        self.intent = intent
        self.payer = payer
        self.transactions = transactions
        self.redirect_urls = redirect_urls


class Payer:
    def __init__(self, payment_method, funding_instruments, payer_info,
                 status):
        self.payment_method = payment_method
        self.funding_instruments = funding_instruments
        self.payer_info = payer_info
        self.status = status
