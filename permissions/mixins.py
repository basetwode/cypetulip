from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.mixins import LoginRequiredMixin as LoginRequired
from django.contrib.contenttypes.models import ContentType

from shop.models.orders import Order, OrderDetail
from shop.models.accounts import Company, Contact


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
        object_instance = self.get_model().objects.filter(**kwargs)

        return self.request.user.is_staff or \
               self.test_anonymous_ownership(**kwargs) or \
               self.test_object_ownership(object_instance, self.field_name) or \
               self.test_order_ownership()

    def test_anonymous_ownership(self, **kwargs):
        if not self.request.user.is_authenticated and self.request.session.session_key:
            object_instance = self.get_model().objects.filter(order__session=self.request.session.session_key, **kwargs)
            return object_instance.count() == 1

    # Used to test for existing objects. Tests whether the contact is set on the given model.
    def test_object_ownership(self, object_instance, field_name):
        if not self.request.user.is_authenticated:
            return False
        is_own_object = getattr(object_instance[0], field_name).id == self.request.user.id if object_instance else False
        if is_own_object:
            return True
        # Test whether the object belongs to another company contact
        contact = Contact.objects.get(user_ptr=self.request.user)
        return Contact.objects \
                   .filter(company=contact.company) \
                   .filter(user_ptr_id=getattr(object_instance[0], field_name).id) \
                   .count() > 0 \
            if object_instance else False

    # Used to test for new objects. Tests whether the contact is set on the order that is related to the new object
    def test_order_ownership(self):
        if self.get_model() is not Order:
            # todo: orderdetails too
            if 'order' in self.kwargs or 'uuid' in self.kwargs:
                order_detail = OrderDetail.objects.filter(order__uuid=self.kwargs[self.get_slug_kwarg()])
                owns_order = self.test_object_ownership(order_detail, 'contact')
                return owns_order
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission_object():
            return self.handle_no_permission()
        return super(PermissionOwnsObjectMixin, self).dispatch(request, *args, **kwargs)


class LoginRequiredMixin(LoginRequired, PermissionPostGetRequiredMixin):
    login_url = 'shop:login'