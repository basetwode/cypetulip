from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.mixins import LoginRequiredMixin as LoginRequired


class LoginRequiredMixin(LoginRequired):
    login_url = 'shop:login'


class PermissionPostGetRequiredMixin(AccessMixin):
    """
    CBV mixin which verifies that the current user has all specified
    permissions.
    """
    permission_post_required = []
    permission_get_required = []
    permission_denied_url = 'permission_denied'

    def get_login_url(self):
        if not self.request.user.is_authenticated:
            return super().get_login_url()
        return self.permission_denied_url or super().get_login_url()

    def get_permission_required(self, method):
        perms = []
        if method == 'POST':
            perms += self.permission_post_required
        else:
            perms += self.permission_get_required
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
    permission_denied_url = 'cms:permission_denied'

    def get_slug_id(self):
        return self.slug_field if self.slug_field else self.id

    def get_id(self):
        return self.id

    def get_model(self):
        return self.model

    def get_slug_kwarg(self):
        return self.slug_url_kwarg

    def get_login_url(self):
        return self.permission_denied_url or super().get_login_url()

    def has_permission(self):
        kwargs = {'{0}'.format(self.get_slug_id()): self.kwargs[self.get_slug_kwarg()]}

        if self.request.user.is_staff or not self.request.user.is_authenticated:
            return True
        object_instance = self.get_model().objects.filter(**kwargs)
        return getattr(object_instance[0], self.field_name).id == self.request.user.id if object_instance else False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()
        return super(PermissionOwnsObjectMixin, self).dispatch(request, *args, **kwargs)
