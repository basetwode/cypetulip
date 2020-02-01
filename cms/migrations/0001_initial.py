# Generated by Django 3.0.2 on 2020-01-15 07:31

import django.core.files.storage
import django.db.models.deletion
import tinymce.models
from django.db import migrations, models

import mediaserver.upload


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CSSSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_color', models.CharField(max_length=6)),
                ('second_color', models.CharField(max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_name', models.CharField(max_length=30)),
                ('position', models.IntegerField()),
                ('is_enabled', models.BooleanField(default=True)),
                ('link', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', tinymce.models.HTMLField(verbose_name='Content')),
                ('picture', models.FileField(blank=True, default=None, null=True,
                                             storage=django.core.files.storage.FileSystemStorage(
                                                 location='/var/cypetulip'),
                                             upload_to=mediaserver.upload.public_files_upload_handler)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.Page')),
            ],
        ),
    ]
