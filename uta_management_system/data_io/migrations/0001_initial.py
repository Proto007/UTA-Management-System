# Generated by Django 4.1.4 on 2022-12-26 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataIO',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(max_length=10000, upload_to='schedules')),
                ('file_type', models.CharField(max_length=10)),
            ],
        ),
    ]
