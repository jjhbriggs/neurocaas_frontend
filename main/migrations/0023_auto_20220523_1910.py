# Generated by Django 2.2.24 on 2022-05-23 19:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20210813_2136'),
    ]

    operations = [
        migrations.RenameField(
            model_name='analysis',
            old_name='groups',
            new_name='groups_TOBEDELETED',
        ),
    ]