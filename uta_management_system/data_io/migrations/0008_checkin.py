# Generated by Django 4.1.4 on 2023-01-01 21:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_io', '0007_randompass_random_pass'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emplid', models.CharField(max_length=8, validators=[django.core.validators.MinLengthValidator(8)])),
                ('late_mins', models.IntegerField(default=0)),
                ('shift', models.ManyToManyField(to='data_io.shift')),
            ],
        ),
    ]
