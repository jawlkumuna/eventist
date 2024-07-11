# Generated by Django 4.2.10 on 2024-07-08 17:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_worldborder'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilmGenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.RenameField(
            model_name='film',
            old_name='banner',
            new_name='backdrop',
        ),
        migrations.AddField(
            model_name='film',
            name='is_adult',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='film',
            name='original_language',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='film',
            name='original_title',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='film',
            name='poster',
            field=models.ImageField(blank=True, null=True, upload_to='film_posters/'),
        ),
        migrations.AddField(
            model_name='film',
            name='release_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='film',
            name='runtime',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='film',
            name='tmdb_popularity',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='film',
            name='tmdb_vote_average',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='film',
            name='tmdb_vote_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='events.location'),
        ),
        migrations.AddField(
            model_name='film',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='films', to='events.filmgenre'),
        ),
    ]
