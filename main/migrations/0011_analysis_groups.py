# Generated by Django 2.2.3 on 2020-05-11 23:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20200511_2301'),
        ('main', '0010_auto_20200511_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='groups',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_list', to='account.AnaGroup'),
        ),
    ]
