# Generated by Django 2.2.24 on 2022-05-20 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20210813_2136'),
        ('account', '0034_auto_20220520_2022'),
    ]

    operations = [
        migrations.AddField(
            model_name='anagroup',
            name='analyses',
            field=models.ManyToManyField(blank=True, null=True, to='main.Analysis'),
        ),
        migrations.AlterField(
            model_name='anagroup',
            name='code',
            field=models.CharField(default='61FB25', max_length=6),
        ),
    ]
