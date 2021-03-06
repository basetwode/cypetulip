
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from rma import buttons

api = {
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
