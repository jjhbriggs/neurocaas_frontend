# Generated by Django 2.2.1 on 2020-10-23 03:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_analysis_custom'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True, help_text='(Read-only) Date/time when record was created.')),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True, help_text='(Read-only) Date/time when record was updated.')),
                ('config_name', models.CharField(help_text='Name of Process', max_length=100, unique=True)),
                ('orig_yaml', models.TextField(blank=True, help_text='Sample yaml config file (leave sample values entered)', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='analysis',
            name='config_template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.ConfigTemplate'),
        ),
    ]
