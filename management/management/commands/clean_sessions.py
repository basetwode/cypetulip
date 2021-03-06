from django.contrib.sessions.models import Session
from django.core import management
from django.core.management import BaseCommand
from django.utils import timezone

from shop.models.orders import OrderDetail
from shop.models.accounts import Company, Contact, Address


class Command(BaseCommand):
    help = "Cleans session table as well as any shopping carts associated with these expired sessions"

    def handle(self, *args, **kwargs):
        inactive_sessions = Session.objects.filter(expire_date__lte=timezone.now())
        inactive_orders = OrderDetail.objects.filter(session__in=inactive_sessions, state__isnull=True)
        inactive_contacts = Contact.objects.filter(session__in=inactive_sessions)
        inactive_addresses = Address.objects.filter(contact__in=inactive_contacts)
        company_list = inactive_contacts.values_list('company', flat=True)
        inactive_companies = Company.objects.filter(id__in=company_list)
        print(str(inactive_sessions.count()) + ", " + str(inactive_orders.count()) + ", " + str(
            inactive_addresses.count()))
        inactive_companies.delete()
        inactive_orders.delete()
        management.call_command('clearsessions', verbosity=0)
