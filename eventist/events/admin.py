from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import Comment
from .models import Download
from .models import Event
from .models import Film
from .models import Host
from .models import Location
from .models import WorldBorder
from .models import Tag
from .models import Cookie, CookieSet

class CookieInline(admin.StackedInline):
    model = Cookie
    extra = 0


@admin.register(CookieSet)
class CookieSetAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [CookieInline,]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {'slug': ('name',), }


@admin.register(Event)
class EventAdmin(SimpleHistoryAdmin):
    list_display = ("title", "location", "start_date", "interested", "going", "first_film")
    list_filter = ("location", "organizers")
    search_fields = ("title", "description")
    autocomplete_fields = ("films", "organizers", "parent_event", "tags",)


@admin.register(WorldBorder)
class WorldBorderAdmin(GISModelAdmin):
    list_display = ("name", "area", "pop2005", "region", "subregion")
    search_fields = ("name", "region", "subregion")
    list_filter = ("region", "subregion")


@admin.register(Host)
class HostAdmin(SimpleHistoryAdmin):
    list_display = ("name", "facebook_link", "starred", "past_event_count")
    search_fields = ("name", "description", "facebook_id",)
    list_filter = ("starred",)
    autocomplete_fields = ("auto_add_tags",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("text", "published")
    search_fields = ("text",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "address")
    search_fields = ("name", "address")


class EventInline(admin.StackedInline):
    model = Film.events.through
    extra = 3
    max_num = 10

class GenresInline(admin.StackedInline):
    model = Film.genres.through
    extra = 3
    max_num = 10


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "runtime")
    search_fields = ("title", "year")
    inlines = (EventInline,GenresInline)


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "md5sum", "size", "download_date")
    search_fields = ("title", "url", "md5sum")
