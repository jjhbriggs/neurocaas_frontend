# Generated by Django 2.2.1 on 2020-10-23 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0023_auto_20201023_0347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anagroup',
            name='code',
            field=models.CharField(default='094DCB', max_length=6),
        ),
    ]
