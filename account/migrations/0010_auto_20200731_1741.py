# Generated by Django 2.2.1 on 2020-07-31 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_user_has_migrated_pwd'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Flag for administrator account'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Flag for administrator account'),
        ),
    ]
