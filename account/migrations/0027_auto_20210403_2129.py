# Generated by Django 2.2.1 on 2021-04-03 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0026_auto_20210331_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anagroup',
            name='code',
            field=models.CharField(default='72F497', max_length=6),
        ),
    ]
