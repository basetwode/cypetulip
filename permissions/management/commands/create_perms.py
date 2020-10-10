from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

GROUPS = ['client', 'client supervisor', 'staff']
MODELS_CLIENT = ['order', 'contact', 'address', 'company', '', 'client']
PERMISSIONS = ['view', ]  # For now only view permission by default for all, others include add, delete, change


class Command(BaseCommand):
    help = "Sends an email to every user, subscribed for notifications on orders due in less than 3 days"

    def handle(self, *args, **kwargs):

        Permission.objects.filter(codename='view_orders').delete()

        content_type = ContentType.objects.get(app_label='shop', model='order')
        print(content_type)
        permission = Permission.objects.get_or_create(
            codename='view_orders',
            name='Can View Own Orders',
            content_type=content_type,
        )
        permission = Permission.objects.get_or_create(
            codename='view_my_account',
            name='Can View My Account',
            content_type=content_type,
        )
        client_group, created = Group.objects.get_or_create(name='client')
        client_supervisor_group, created = Group.objects.get_or_create(name='client supervisor')
        staff_group, created = Group.objects.get_or_create(name='staff')

        # View perms
        perm_view_orders = Permission.objects.get(codename='view_orders')
        perms_view_my_account = Permission.objects.get(codename='view_my_account')

        # Address perms
        perm_add_address = Permission.objects.get(codename='add_address')
        perm_change_address = Permission.objects.get(codename='change_address')
        perm_delete_address = Permission.objects.get(codename='delete_address')
        perm_view_address = Permission.objects.get(codename='view_address')

        # Company perms
        perm_add_company = Permission.objects.get(codename='add_company')
        perm_change_company = Permission.objects.get(codename='change_company')
        perm_view_company = Permission.objects.get(codename='view_company')

        # Contact perms
        perm_change_contact = Permission.objects.get(codename='change_contact')
        perm_view_contact = Permission.objects.get(codename='view_contact')

        print(client_group)

        client_group_permissions = (perm_view_orders, perms_view_my_account,
                                    perm_view_company, perm_view_contact,
                                    perm_view_address)

        client_group.permissions.set(client_group_permissions)
        client_group.save()

        client_supervisor_group.permissions.set(client_group_permissions)
        client_supervisor_group.permissions.add(perm_add_address)
        client_supervisor_group.permissions.add(perm_change_address)
        client_supervisor_group.permissions.add(perm_delete_address)
        client_supervisor_group.permissions.add(perm_add_company)
        client_supervisor_group.permissions.add(perm_change_company)
        client_supervisor_group.permissions.add(perm_change_contact)
        client_supervisor_group.save()

        permissions_list = Permission.objects.all()
        staff_group.permissions.set(permissions_list)
        staff_group.save()