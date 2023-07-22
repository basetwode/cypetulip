from django.apps import AppConfig
from rma.view_api import view_api


class RMAConfig(AppConfig):
    name = 'rma'
    api = view_api

    def ready(self):

        print("Loading rma appconfig")
        try:
            from rma.models.main import ReturnMerchandiseAuthorizationConfig, ReturnMerchandiseAuthorizationShipper, \
                ReturnMerchandiseAuthorizationState
            from django.contrib.auth.models import Group, Permission
            from django.contrib.contenttypes.models import ContentType

            rma_config = ReturnMerchandiseAuthorizationConfig.objects.first()
            if not rma_config:
                rma_config = ReturnMerchandiseAuthorizationConfig()
                rma_config.save()
            # Default shipper
            shipper = ReturnMerchandiseAuthorizationShipper.objects.get_or_create(shipper__isnull=True)
            end_state, created = ReturnMerchandiseAuthorizationState.objects.get_or_create(name="Received", is_end_state=True)
            cancelled_state, created = ReturnMerchandiseAuthorizationState.objects.get_or_create(name="Cancelled")
            accepted_state, created = ReturnMerchandiseAuthorizationState.objects.get_or_create(name="Accepted",
                                                                                       cancel_rma_state=cancelled_state,
                                                                                       next_state=end_state)
            initial_state, created = ReturnMerchandiseAuthorizationState.objects.get_or_create(name="Open", initial=True, next_state=accepted_state,
                                                                cancel_rma_state=cancelled_state)

            client_supervisor_group = Group.objects.get(name='client supervisor')

            permission_view_rma = Permission.objects.get(
                codename='view_returnmerchandiseauthorization',
            )
            client_supervisor_group.permissions.add(permission_view_rma)
            client_supervisor_group.save()
        except Exception as error:
            print("DB not migrated")
