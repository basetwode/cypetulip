# Generated by Django 3.0.2 on 2020-01-15 07:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('street', models.CharField(default=None, max_length=40)),
                ('number', models.CharField(default=None, max_length=5)),
                ('zipcode', models.CharField(default=None, max_length=5)),
            ],
        ),
        migrations.RemoveField(
            model_name='productsubitem',
            name='special_price',
        ),
    ]
