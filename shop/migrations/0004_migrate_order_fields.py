from django.db import migrations


def migrate(apps, schema_editor):
    OrderDetail = apps.get_model('shop', 'OrderDetail')
    for row in OrderDetail.objects.all():
        row.company = row.order.company
        row.individual_offer_request = row.order.individual_offer_request
        row.is_send = row.order.is_send
        row.session = row.order.session
        row.uuid = row.order.uuid
        row.save()


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0003_auto_20210306_1920'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(migrate),
    ]
