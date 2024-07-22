from django.urls import path

from . import views

app_name = "events"
urlpatterns = [
    path("", views.home_view, name="home"),
    path("events/", views.EventListView.as_view(), name="events"),
    path("events/<int:pk>/", views.EventView.as_view(), name="event_detail"),
    path("hosts/", views.HostListView.as_view(), name="hosts"),
    path("hosts/<int:pk>/", views.host_view, name="host_detail"),
    path("films/", views.FilmListView.as_view(), name="films"),
    path("films/<int:pk>/", views.film_details, name="film_detail"),
    path("tags/", views.tag_list, name="tags"),
    path("tags/<int:pk>/", views.tag_details, name="tag_detail"),
    path("scrapeevent/<int:id>/", views.scrape_event_view, name="scrapeEvent"),
    path(
        "scrapehostfuture/<path:host>/",
        views.scrape_host_future,
        name="scrapeHostFuture",
    ),
    path("scrapehostpast/<path:host>/", views.scrape_host_past, name="scrapeHostPast"),
    path("findfilm/<int:event_id>/", views.find_film_view, name="findFilm"),
    path("findfilms/", views.find_films_view, name="findFilms"),

    path("reloadtags/", views.reload_tags, name="reloadTags"),
    path("search/", views.search_view, name="search"),

    path("loadartmozi/", views.load_artmozi_view, name="loadArtmozi"),
    path("loadstarred/", views.load_starred_view, name="loadStarred"),
]
