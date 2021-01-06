from django.utils import timezone


def rma_init_available(order_hash):
    from datetime import timedelta, datetime
    from rma.models import ReturnMerchandiseAuthorizationConfig
    from shop.models import OrderDetail
    order = OrderDetail.objects.get(order__order_hash=order_hash)
    config = ReturnMerchandiseAuthorizationConfig.objects.first()
    is_eligible = (order.date_bill + timedelta(days=config.retention_time) > timezone.now()) if order.date_bill else True
    return is_eligible
