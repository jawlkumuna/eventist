from eventist.events.models import Event, Film, FilmGenre, Host
import requests
from django.utils.http import urlencode
from django.core.files.base import ContentFile
import re
from config.settings.base import env


headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {env.str('TMDB_API_KEY')}"
}


def find_films():
    for event in Host.objects.get(name="Bem Mozi").events.all():
        print(event.title)
        if event.films.count() > 0:
            continue
        try:
            find_film(event.id)
        except Exception as e:
            print(e)


def find_film(event_id):
    event = Event.objects.get(pk=event_id)
    if event.films.count() > 0:
        return event.films.first()
    else:
        # find year in description
        year = re.search(r"\b(19|20)\d{2}\b", event.description or "")
        year = year.group(0) if year else None

        params = {"query": event.title,
                  "include_adult": False, "language": "en-US", "page": 1,}

        if year:
            params["primary_release_year"] = year

        url = "https://api.themoviedb.org/3/search/movie?"
        url += urlencode(params)
        response = requests.get(url, headers=headers).json()
        print(url)
        print(response["results"])
        if len(response["results"]) == 0:
            return
        # select most popular movie
        movie = max(response["results"], key=lambda x: x["popularity"])
        film, created = Film.objects.get_or_create(
            title=movie["title"],
            tmdb_id=movie["id"],
        )

        if created:
            details = requests.get(
                f"https://api.themoviedb.org/3/movie/{film.tmdb_id}?language=en-US", headers=headers).json()
            if movie["release_date"]:
                film.release_date = movie["release_date"]
            film.runtime = details["runtime"]
            film.description = movie["overview"]
            film.tmdb_popularity = movie["popularity"]
            film.tmdb_vote_average = movie["vote_average"]
            film.tmdb_vote_count = movie["vote_count"]
            film.is_adult = movie["adult"]
            film.original_language = movie["original_language"]
            film.original_title = movie["original_title"]
            film.imdb_id = details["imdb_id"]

            film.poster.save(
                f"{film.title}_poster.jpg",
                ContentFile(requests.get(
                    f"https://image.tmdb.org/t/p/original{details['poster_path']}").content),
            )

            film.backdrop.save(
                f"{film.title}_backdrop.jpg",
                ContentFile(requests.get(
                    f"https://image.tmdb.org/t/p/original{details['backdrop_path']}").content),
            )

            film.save()

            for genre in details["genres"]:
                film_genre, _ = FilmGenre.objects.get_or_create(
                    name=genre["name"])
                film.genres.add(film_genre)

        event.films.add(film)
        event.save()
