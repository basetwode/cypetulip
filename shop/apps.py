from django.apps import AppConfig, apps

from utils.apps import BaseConfig


class WebappConfig(BaseConfig):
    name = 'shop'

    def ready(self):
        try:

            from shop.models.accounts import Contact
            from shop.models.accounts import Company
            admin_company, created = Company.objects.get_or_create(name="Admin", street="Admin",
                                                         number="Admin",zipcode="Admin",city="Admin")
            admin_contact, created = Contact.objects.get_or_create(username="admin", company=admin_company)
            if created:
                admin_contact.set_password("admin")
                admin_contact.is_superuser = True
                admin_contact.is_staff = True
                admin_contact.save()

            from shop.models.orders import OrderState
            from management.models.models import LegalSetting
            legal_settings = LegalSetting.objects.all()
            if legal_settings.count() ==0:
                ls = LegalSetting(company_name="Shop", street="")
                ls.save()
            from management.models.models import CacheSetting
            cache_settings = CacheSetting.objects.all()
            if cache_settings.count() ==0:
                cs = CacheSetting(css_js_cache_enabled=False, cache_clear_required=False)
                cs.save()
            init_state = OrderState.objects.filter(initial=True)
            if init_state.count() == 0:
                cancel_state = OrderState(name="Cancelled")
                cancel_state.save()
                sent_state = OrderState(name="Sent", is_sent_state=True, cancel_order_state=cancel_state)
                sent_state.save()
                paid_state = OrderState(name="Paid", is_paid_state=True, cancel_order_state=cancel_state,
                                        next_state=sent_state)
                paid_state.save()
                in_work_state = OrderState(name="Processing", cancel_order_state=cancel_state, next_state=paid_state)
                in_work_state.save()
                init_state = OrderState(initial=True, name="Open", cancel_order_state=cancel_state,
                                        next_state=in_work_state)
                init_state.save()

        except Exception as e:
            print("DB not migrated")
        super(WebappConfig, self).ready()

