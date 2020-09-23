# Generated by Django 2.2.1 on 2020-08-04 22:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_user_requested_group_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='anagroup',
            name='code',
            field=models.CharField(blank=True, default='HSP29V', editable=False, max_length=6),
        ),
        migrations.AlterField(
            model_name='user',
            name='requested_group_name',
            field=models.CharField(default='', max_length=50, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')]),
        ),
    ]