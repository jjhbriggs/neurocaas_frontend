# Generated by Django 2.2.3 on 2020-05-27 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20200527_0249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='demo_link',
            field=models.CharField(blank=True, help_text='Link of Demo page', max_length=100, null=True),
        ),
    ]
