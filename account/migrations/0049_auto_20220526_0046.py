# Generated by Django 2.2.24 on 2022-05-26 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0048_auto_20220525_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='iam',
            name='fixed_creds',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='anagroup',
            name='code',
            field=models.CharField(default='C86183', max_length=6),
        ),
    ]