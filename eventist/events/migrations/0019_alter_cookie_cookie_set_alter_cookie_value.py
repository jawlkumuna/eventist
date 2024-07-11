# Generated by Django 5.0.7 on 2024-07-10 10:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_cookieset_cookie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cookie',
            name='cookie_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cookies', to='events.cookieset'),
        ),
        migrations.AlterField(
            model_name='cookie',
            name='value',
            field=models.CharField(max_length=256),
        ),
    ]
