# Generated by Django 4.2.10 on 2024-06-03 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_historicalhost_starred_host_starred'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalhost',
            name='facebook_id',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='facebook_id',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
