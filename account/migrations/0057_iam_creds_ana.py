# Generated by Django 2.2.24 on 2022-05-31 00:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20220523_1910'),
        ('account', '0056_auto_20220530_2344'),
    ]

    operations = [
        migrations.AddField(
            model_name='iam',
            name='creds_ana',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.Analysis'),
        ),
    ]
