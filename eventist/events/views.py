from django.http import HttpResponse
from django.views import generic
from django.utils import timezone

from eventist.events.tasks import scrape_event
from eventist.events.tasks import scrape_events_by_host
from eventist.events.tasks.tmdb import find_film, find_films
from eventist.events.tasks.tags import find_tags_for_all_events
from eventist.events.tasks.artmozi import load_artmozi
from django.db.models import Q
from django.shortcuts import render
from .models import Event, Host, Film
from django.core.paginator import Paginator

# Create your views here.


def load_artmozi_view(request):
    load_artmozi.delay()
    return HttpResponse("Artmozi events loaded")


def search_view(request):
    page = request.GET.get("page", 1)
    q = request.GET.get("q")
    events = Event.objects.filter(Q(title__icontains=q) | Q(
        description__icontains=q)).order_by("-interested")
    paginator = Paginator(events, per_page=15)
    page_object = paginator.get_page(page)
    page_object.adjusted_elided_pages = paginator.get_elided_page_range(
        page, on_each_side=2, on_ends=1)

    return render(request, "events/search.html", {"page_obj": page_object, "q": q})


def reload_tags(request):
    find_tags_for_all_events()
    return HttpResponse("Tags reloaded")


def scrape_event_view(request, id):
    scrape_event.delay(id, forceDownload=True)
    return HttpResponse("Event scraped")


def scrape_host_future(request, host):
    scrape_events_by_host.delay(host)
    return HttpResponse("Host scraped")


def scrape_host_past(request, host):
    scrape_events_by_host.delay(host, past=True)
    return HttpResponse("Host scraped")


def find_film_view(request, event_id):
    find_film(event_id)
    return HttpResponse("Film found")


def find_films_view(request):
    find_films()
    return HttpResponse("Film found")


def home_view(request):
    upcoming = Event.objects.filter(
        cinema=False, start_date__gte=timezone.now()).order_by("start_date")[:6]
    ongoing = Event.objects.filter(cinema=False, start_date__lte=timezone.now(
    ), end_date__gte=timezone.now()).order_by("start_date")[:6]

    films_today = []
    # TODO write proper query for this
    for film in Film.objects.all():
        for event in film.events.all():
            if event.start_date.date() == timezone.now().date() and event.start_date >= timezone.now():
                films_today.append(film)
                break

    ctx = {
        "upcoming": upcoming,
        "ongoing": ongoing,
        "films_today": films_today[:12]
    }
    return render(request, "events/home.html", context=ctx)


class EventListView(generic.ListView):
    model = Event
    queryset = Event.objects.filter(
        cinema=False, start_date__gte=timezone.now()).order_by("start_date")
    paginate_by = 21
    template_name = "events/event_list.html"


def event_list_view(request):
    page = request.GET.get("page", 1)
    events = Event.objects.filter(
        cinema=False, start_date__gte=timezone.now()).order_by("start_date")
    paginator = Paginator(events, per_page=21)
    page_object = paginator.get_page(page)
    return render(request, "event_list.html", {"page_obj": page_object})


class EventView(generic.DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"


class HostListView(generic.ListView):
    model = Host
    paginate_by = 24
    queryset = Host.objects.order_by("-past_event_count")
    template_name = "events/host_list.html"


class HostView(generic.DetailView):
    model = Host
    template_name = "events/host_detail.html"
    context_object_name = "event"


def host_view(request, pk):
    host = Host.objects.get(pk=pk)
    upcoming = host.events.filter(
        cinema=False, start_date__gte=timezone.now()).order_by("start_date")
    past = host.events.filter(
        cinema=False, start_date__lte=timezone.now()).order_by("-start_date")
    return render(request, "events/host_detail.html", {"object": host, "upcoming": upcoming, "past": past})


class FilmListView(generic.ListView):
    model = Film
    paginate_by = 24
    template_name = "events/film_list.html"

# class FilmView(generic.DetailView):
#     model = Film
#     template_name = "events/film_detail.html"


def film_details(request, pk):
    film = Film.objects.get(pk=pk)
    screenings = film.events.filter(
        start_date__gte=timezone.now()).order_by("start_date")
    return render(request, "events/film_detail.html", {"object": film, "screenings": screenings})
