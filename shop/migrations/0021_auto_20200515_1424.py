# Generated by Django 3.0.2 on 2020-05-15 12:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0020_orderdetail_shipment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='session',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='shop.Company'),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='shop.Contact'),
        ),
    ]