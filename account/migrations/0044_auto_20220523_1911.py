# Generated by Django 2.2.24 on 2022-05-23 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0043_auto_20220523_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anagroup',
            name='code',
            field=models.CharField(default='6ACA42', max_length=6),
        ),
    ]