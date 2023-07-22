from django.apps import AppConfig
from django.apps import apps


class WebappConfig(AppConfig):
    name = 'permissions'
    api = {}

    def ready(self):
        print("Loading permissions appconfig")
        try:
            from django.contrib.auth.models import Permission, Group
            from django.contrib.contenttypes.models import ContentType

            content_type, _ = ContentType.objects.get_or_create(app_label='shop', model='order')
            content_type_mgmt, _ = ContentType.objects.get_or_create(app_label='management', model='shopsetting')
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
            permission_mgmt = Permission.objects.get_or_create(
                codename='view_management',
                name='Can View Management',
                content_type=content_type_mgmt,
            )
            permission_mgmt = Permission.objects.get_or_create(
                codename='view_generic',
                name='Can View Management',
                content_type=content_type_mgmt,
            )
            permission_mgmt = Permission.objects.get_or_create(
                codename='change_generic',
                name='Can View Management',
                content_type=content_type_mgmt,
            )

            app_names = ['management','shop','billing','payment','cms','mediaserver','permissions',
                    'shipping','accounting','utils']
            permissions_list_mgmt = ['view','change']

            ctmgmt, created =  ContentType.objects.get_or_create(app_label='management', model='generic')
            for app_name in app_names:
                models = apps.all_models[app_name]
                for model in models:
                    for permission_name in permissions_list_mgmt:
                        permission_mgmt = Permission.objects.get_or_create(
                            codename=permission_name+'_'+model,
                            name=f"Can {permission_name.capitalize()} {model}",
                            content_type=ctmgmt,
                        )

            client_group, created = Group.objects.get_or_create(name='client')
            client_supervisor_group, created = Group.objects.get_or_create(name='client supervisor')
            staff_group, created = Group.objects.get_or_create(name='staff')

            # View perms
            perm_view_orders = Permission.objects.get(codename='view_orders',content_type__app_label='shop')
            perms_view_my_account = Permission.objects.get(codename='view_my_account',content_type__app_label='shop')

            # Address perms
            perm_add_address = Permission.objects.get(codename='add_address',content_type__app_label='shop')
            perm_change_address = Permission.objects.get(codename='change_address',content_type__app_label='shop')
            perm_delete_address = Permission.objects.get(codename='delete_address',content_type__app_label='shop')
            perm_view_address = Permission.objects.get(codename='view_address',content_type__app_label='shop')

            # Company perms
            perm_add_company = Permission.objects.get(codename='add_company',content_type__app_label='shop')
            perm_change_company = Permission.objects.get(codename='change_company',content_type__app_label='shop')
            perm_view_company = Permission.objects.get(codename='view_company',content_type__app_label='shop')

            # Contact perms
            perm_change_contact = Permission.objects.get(codename='change_contact',content_type__app_label='shop')
            perm_view_contact = Permission.objects.get(codename='view_contact',content_type__app_label='shop')

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
        except Exception as error:
            print("DB not migrated")
