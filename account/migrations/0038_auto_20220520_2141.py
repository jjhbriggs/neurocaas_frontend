# Generated by Django 2.2.24 on 2022-05-20 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0037_auto_20220520_2037'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='anagroup',
            options={'verbose_name': 'Group', 'verbose_name_plural': 'Groups'},
        ),
        migrations.AddField(
            model_name='user',
            name='cred_expire',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='anagroup',
            name='code',
            field=models.CharField(default='C44BEC', max_length=6),
        ),
    ]
