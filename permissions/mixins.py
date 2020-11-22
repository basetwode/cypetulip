from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.mixins import LoginRequiredMixin as LoginRequired
from django.contrib.contenttypes.models import ContentType


class PermissionPostGetRequiredMixin(AccessMixin):
    """
    CBV mixin which verifies that the current user has all specified
    permissions.
    """
    permission_post_required = []
    permission_get_required = []
    permission_denied_url = 'permissions:permission_denied'

    def get_login_url(self):
        if not self.request.user.is_authenticated:
            return super().get_login_url()
        return self.permission_denied_url or super().get_login_url()

    def get_permission_get_required(self):
        if len(self.permission_get_required) == 0 and hasattr(self, 'model') and self.model:
            ct = ContentType.objects.get_for_model(self.model)
            if self.request.path[1:].startswith('shop'):
                return [ct.app_label+'.'+'view_'+ct.model]
            else:
                return ['management.'+'view_'+ct.model]
        elif len(self.permission_get_required) == 0 and not self.request.path[1:].startswith('shop'):
            return ['management.'+'view_generic']
        else:
            return self.permission_get_required

    def get_permission_post_required(self):
        if len(self.permission_post_required) == 0 and hasattr(self, 'model') and self.model:
            ct = ContentType.objects.get_for_model(self.model)
            if self.request.path[1:].startswith('shop'):
                return [ct.app_label+'.'+'view_'+ct.model]
            else:
                return ['management.'+'view_'+ct.model]
        elif len(self.permission_post_required) == 0 and not self.request.path[1:].startswith('shop'):
            return ['management.'+'change_generic']
        else:
            return self.permission_post_required

    def get_permission_required(self, method):
        perms = []
        if method == 'POST':
            perms += self.get_permission_post_required()
        else:
            perms += self.get_permission_get_required()
        return perms

    def has_permission(self, method):
        perms = self.get_permission_required(method)
        return self.request.user.has_perms(perms)

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request.method):
            return self.handle_no_permission()
        return super(PermissionPostGetRequiredMixin, self).dispatch(request, *args, **kwargs)


class PermissionOwnsObjectMixin(AccessMixin):
    id = None
    model = None
    field_name = ""
    slug_field = ""
    slug_url_kwarg = ""
    permission_denied_url = 'permissions:permission_denied'
    login_url = 'shop:login'

    def get_slug_id(self):
        return self.slug_field if self.slug_field else self.id

    def get_id(self):
        return self.id

    def get_model(self):
        return self.model

    def get_slug_kwarg(self):
        return self.slug_url_kwarg

    def get_login_url(self):
        return self.permission_denied_url

    def has_permission_object(self):
        kwargs = {'{0}'.format(self.get_slug_id()): self.kwargs[self.get_slug_kwarg()]}

        if self.request.user.is_staff:
            return True
        if not self.request.user.is_authenticated:
            object_instance = self.get_model().objects.filter(order__session=self.request.session.session_key, **kwargs)
            return object_instance.count() == 1

        object_instance = self.get_model().objects.filter(**kwargs)
        return getattr(object_instance[0], self.field_name).id == self.request.user.id if object_instance else False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission_object():
            return self.handle_no_permission()
        return super(PermissionOwnsObjectMixin, self).dispatch(request, *args, **kwargs)


class LoginRequiredMixin(LoginRequired, PermissionPostGetRequiredMixin):
    login_url = 'shop:login'