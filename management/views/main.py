from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
# Create your views here.
from django.views.generic import TemplateView

from permissions.mixins import LoginRequiredMixin
from shop.models.accounts import Contact


class ManagementView(LoginRequiredMixin, TemplateView):
    permission_get_required = ['management.view_management']
    template_name = 'management/management.html'

    def get_context_data(self, **kwargs):
        contact = Contact.objects.filter(user_ptr=self.request.user)
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        user_id_list = [data.get_decoded().get('_auth_user_id', None) for data in active_sessions]
        users = User.objects.filter(id__in=user_id_list)

        return {**super(ManagementView, self).get_context_data(), **{'contact': contact, 'users': users,
                                                                     'active_sessions': Session.objects.filter(
                                                                         expire_date__gte=timezone.now())}}
