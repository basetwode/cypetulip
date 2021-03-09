from django.db import migrations


def migrate(apps, schema_editor):
    PaymentDetail = apps.get_model('payment', 'PaymentDetail')
    for row in PaymentDetail.objects.all():
        row.order_detail = row.order.orderdetail_set.first()
        row.save()


class Migration(migrations.Migration):
    dependencies = [
        ('payment', '0003_paymentdetail_order_detail'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(migrate),
    ]
