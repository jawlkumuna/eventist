import requests
from datetime import datetime
from celery import shared_task
from ..models import Event, Host

CINEMACITY_CINEMAS = {
    1124: "Cinema City - Alba - Székesfehérvár",
    1133: "Cinema City - Allee - Budapest",
    1132: "Cinema City - Arena - Budapest",
    1131: "Cinema City - Balaton - Veszprém",
    1139: "Cinema City - Campona - Budapest",
    1127: "Cinema City - Debrecen",
    1141: "Cinema City - Duna Pláza - Budapest",
    1125: "Cinema City - Győr",
    1144: "Cinema City - Mammut I-II. - Budapest",
    1129: "Cinema City - Miskolc",
    1143: "Cinema City - Nyíregyháza",
    1128: "Cinema City - Pécs",
    1134: "Cinema City - Savaria - Szombathely",
    1136: "Cinema City - Sopron",
    1126: "Cinema City - Szeged",
    1130: "Cinema City - Szolnok",
    1137: "Cinema City - Westend - Budapest",
    1135: "Cinema City - Zalaegersze",
}


@shared_task()
def load_cinemacity():
    Event.objects.filter(title__contains='Cinema City').delete()
    for cinema in CINEMACITY_CINEMAS:
        resp = requests.get(f'https://www.cinemacity.hu/hu/data-api-service/v1/quickbook/10102/film-events/in-cinema/{cinema}/at-date/2024-06-03')
        data = resp.json()
        movies = {}
        for m in data['body']['films']:
            print(m['name'])
            movies[m['id']] = {'title': m['name'], 'poster': m['posterLink']}

        for screening in data['body']['events']:
            print('----')
            print(movies[screening['filmId']]['title'], screening['eventDateTime'], CINEMACITY_CINEMAS[cinema])

            # add to DB
            date_time = datetime.strptime(screening['eventDateTime'], "%Y-%m-%dT%H:%M:%S")
            event = Event(
                title=f'{movies[screening['filmId']]['title']} | {CINEMACITY_CINEMAS[cinema]}',
                start_date=date_time,
            )
            event.save()
            host, _ = Host.objects.get_or_create(name=CINEMACITY_CINEMAS[cinema])
            event.organizers.add(host)
