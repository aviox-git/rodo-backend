# Generated by Django 2.2.1 on 2019-05-27 06:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20190527_0559'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='ordertoken',
        ),
        migrations.DeleteModel(
            name='OrderToken',
        ),
    ]
