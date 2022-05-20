# Generated by Django 2.2.24 on 2022-05-19 20:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0032_auto_20210813_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.AnaGroup'),
        ),
        migrations.AlterField(
            model_name='anagroup',
            name='code',
            field=models.CharField(default='E8A8A9', max_length=6),
        ),
    ]
