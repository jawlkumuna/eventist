# Generated by Django 4.2.10 on 2024-06-03 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_event_films'),
    ]

    operations = [
        migrations.CreateModel(
            name='Download',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=2048, null=True)),
                ('url', models.URLField()),
                ('download_date', models.DateTimeField(auto_now_add=True)),
                ('playwright_rendered', models.BooleanField(default=False)),
                ('content_type', models.CharField(blank=True, max_length=100, null=True)),
                ('content', models.FileField(upload_to='downloads/')),
                ('scroll_amount', models.IntegerField(blank=True, null=True)),
                ('md5sum', models.CharField(blank=True, max_length=32, null=True)),
            ],
        ),
    ]
