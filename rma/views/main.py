from permissions.views.mixins import LoginRequiredMixin
from rma.models.main import ReturnMerchandiseAuthorization
from shop.models.orders import OrderDetail
from utils.views import CreateUpdateView


class RMAInitView(LoginRequiredMixin, CreateUpdateView):
    template_name = 'rma/account/account-rma-create.html'
    model = ReturnMerchandiseAuthorization
    slug_url_kwarg = 'uuid'
    slug_field = 'order'
    fields = ['shipper']

    # todo make sure that this view is protected and that others can not create rmas for any orders

    def get_context_data(self, **kwargs):
        return {**super(RMAInitView, self).get_context_data(**kwargs),
                **{'order': OrderDetail.objects.get(company=self.request.user.contact.company, uuid=self.kwargs['uuid'])}}

    def form_valid(self, form):
        # todo build form manually and show description of selected shipper and add orderitem select
        # todo set defaults on save (eg. contact,...)
        # todo select orderitem too
        print('asd')
