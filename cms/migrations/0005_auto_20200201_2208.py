# Generated by Django 3.0.2 on 2020-02-01 21:08

import django.core.files.storage
from django.db import migrations, models

import mediaserver.upload


class Migration(migrations.Migration):
    dependencies = [
        ('cms', '0004_auto_20200130_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='picture',
            field=models.FileField(blank=True, default=None, null=True,
                                   storage=django.core.files.storage.FileSystemStorage(location='/var/cypetulip'),
                                   upload_to=mediaserver.upload.public_files_upload_handler),
        ),
    ]
