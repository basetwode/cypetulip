from django.apps import AppConfig


from rma.api import api


class RMAConfig(AppConfig):
    name = 'rma'
    api = api

    def ready(self):
        try:
            from rma.models.main import ReturnMerchandiseAuthorizationConfig, ReturnMerchandiseAuthorizationShipper, \
                ReturnMerchandiseAuthorizationState
            rma_config = ReturnMerchandiseAuthorizationConfig.objects.first()
            if not rma_config:
                rma_config = ReturnMerchandiseAuthorizationConfig()
                rma_config.save()
            # Default shipper
            shipper = ReturnMerchandiseAuthorizationShipper.objects.get_or_create(shipper__isnull=True)
            end_state = ReturnMerchandiseAuthorizationState.objects.get_or_create(name="Received", is_end_state=True)
            cancelled_state = ReturnMerchandiseAuthorizationState.objects.get_or_create(name="Cancelled")
            accepted_state = ReturnMerchandiseAuthorizationState.objects.get_or_create(name="Accepted",
                                                                                       cancel_rma_state=cancelled_state,
                                                                                       next_state=end_state)
            initial_state = ReturnMerchandiseAuthorizationState(name="Open", initial=True, next_state=accepted_state,
                                                                cancel_rma_state=cancelled_state)

        except Exception as error:
            print("DB not migrated")
