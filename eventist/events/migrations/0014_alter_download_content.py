# Generated by Django 4.2.10 on 2024-06-07 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_alter_historicallocation_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='download',
            name='content',
            field=models.FileField(max_length=4096, upload_to='downloads/'),
        ),
    ]
