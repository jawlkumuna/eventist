import requests
from datetime import datetime
from celery import shared_task
from ..models import Event, Host, Film
from .tmdb import find_film

ARTMOZI_CINEMAS = [
    'corvinmozi',
    'artmozi',
]

ARTMOZI_IDS = {
    1450: "Művész Mozi",
    1448: "Puskin Mozi",
    1449: "Toldi Mozi",
    1451: "Tabán Mozi",
    1452: "Kino Cafe",
    1447: "Corvin Mozi",
}

@shared_task()
def load_artmozi():
    # delete old events
    for cinema in ARTMOZI_IDS.values():
        try:
            Host.objects.get(name=cinema).events.all().delete()
        except:
            pass

    # weeks
    weeks = requests.get('https://artmozi.hu/api/schedule/week').json()['weeks']

    for cinema in ARTMOZI_CINEMAS:
        for week in weeks:
            response = requests.get(
                f'https://{cinema}.hu/api/schedule/week/{week}')
            data = response.json()
            movies = {}
            # unpopulated weeks are present as an empty list in the api
            if type(data['movies']) is not dict:
                continue
            for m in data['movies'].keys():
                print(m, data['movies'][m]['title'])
                movies[m] = {'title': data['movies'][m]['title'].strip(),
                            'poster': data['movies'][m]['webpUrl']}
            for day in data['schedule']:
                date_object = datetime.strptime(day, "%Y%m%d")
                for movie_id in data['schedule'][day]:
                    for start_time in data['schedule'][day][movie_id]:
                        for screening_id in data['schedule'][day][movie_id][start_time]:
                            screening = data['schedule'][day][movie_id][start_time][screening_id]
                            print('----')
                            movie_title = movies[movie_id]['title'].strip()
                            print(movie_title, date_object, start_time, ARTMOZI_IDS[screening['cinema']])

                            # add to DB
                            date_time = datetime.strptime(f'{day} {start_time}', "%Y%m%d %H:%M")
                            screening_place = ARTMOZI_IDS[screening['cinema']]
                            event = Event(
                                title=movie_title,
                                start_date=date_time,
                                cinema=True,
                            )
                            event.save()

                            # film, _ = Film.objects.get_or_create(title=movie_title)
                            # event.films.add(film)
                            host, _ = Host.objects.get_or_create(name=screening_place)
                            event.organizers.add(host)

                            find_film(event.id)
