# Generated by Django 2.1.7 on 2020-04-07 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20200407_0214'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='submit_path',
            field=models.CharField(blank=True, help_text='Path of submit file', max_length=100, null=True),
        ),
    ]
