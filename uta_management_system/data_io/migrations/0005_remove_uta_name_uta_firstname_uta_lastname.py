# Generated by Django 4.1.4 on 2022-12-29 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_io', '0004_uta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uta',
            name='name',
        ),
        migrations.AddField(
            model_name='uta',
            name='firstname',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='uta',
            name='lastname',
            field=models.CharField(default='', max_length=100),
        ),
    ]
