from django.utils.translation import gettext_lazy as _

from rma import buttons

view_api = {
    'shop': {
        'account.orders.order.buttons':
            {
                'rma:init': {
                    'url': 'rma:rma_init',
                    'text': _('Return items'),
                    'is_available': buttons.rma_init_available
                }
            }
    }
}
