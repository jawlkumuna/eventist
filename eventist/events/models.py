from django.contrib.gis.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords
from django.utils.http import urlencode

class CookieSet(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class Cookie(models.Model):
    name = models.CharField(max_length=256)
    value = models.CharField(max_length=256)
    domain = models.CharField(max_length=256, default=".facebook.com")
    path = models.CharField(max_length=256, default="/")
    cookie_set = models.ForeignKey(CookieSet, on_delete=models.CASCADE, related_name="cookies")

    def __str__(self):
        return self.name



class Tag(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256)

    def __str__(self):
        return self.name


class FilmGenre(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Film(models.Model):
    title = models.CharField(max_length=2048)
    year = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    backdrop = models.ImageField(
        null=True, upload_to="film_banners/", blank=True)
    poster = models.ImageField(
        null=True, upload_to="film_posters/", blank=True)
    tmdb_id = models.IntegerField(null=True, blank=True)
    imdb_id = models.CharField(max_length=16, null=True, blank=True)

    genres = models.ManyToManyField(
        FilmGenre, related_name="films", blank=True)
    original_title = models.CharField(max_length=2048, null=True, blank=True)
    original_language = models.CharField(max_length=128, null=True, blank=True)

    tmdb_popularity = models.FloatField(null=True, blank=True)
    tmdb_vote_average = models.FloatField(null=True, blank=True)
    tmdb_vote_count = models.IntegerField(null=True, blank=True)
    is_adult = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.release_date})"


class Host(models.Model):
    name = models.CharField(max_length=512)
    starred = models.BooleanField(default=False)
    facebook_id = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    past_event_count = models.IntegerField(default=0, blank=True)
    profile_picture = models.ImageField(
        null=True,
        upload_to="profile_pictures/",
        blank=True,
    )
    history = HistoricalRecords()

    # each event organized by this host will have these tags added
    auto_add_tags = models.ManyToManyField(
        Tag, related_name="auto_adder_hosts", blank=True)

    def __str__(self):
        return self.name

    @property
    def facebook_link(self):
        return f"https://facebook.com/{self.facebook_id}"


class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)
    banner = models.ImageField(null=True, upload_to="banners/", blank=True)
    location = models.ForeignKey(
        "Location",
        related_name="events",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(null=True, blank=True)
    interested = models.IntegerField(default=0, blank=True)
    going = models.IntegerField(default=0, blank=True)
    organizers = models.ManyToManyField(
        Host, related_name="events", blank=True)
    films = models.ManyToManyField(Film, related_name="events", blank=True)
    parent_event = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subevents",
    )

    source = models.CharField(max_length=100, null=True, blank=True)
    source_url = models.URLField(
        verbose_name="Source URL",
        max_length=256,
        null=True,
        blank=True,
    )
    cinema = models.BooleanField(default=False)
    fully_scraped = models.BooleanField(default=False)

    tags = models.ManyToManyField(Tag, related_name="events", blank=True)

    date_added = models.DateTimeField(auto_now_add=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, null=True)

    history = HistoricalRecords()

    def relative_date_string(self):
        if self.start_date.date() == timezone.now().date():
            return "(TODAY)"
        elif self.start_date.date() == timezone.now().date() + timezone.timedelta(days=1):
            return "(TOMORROW)"
        return ""

    def first_film(self):
        if self.films.count() > 0:
            return self.films.first()
        return None

    def past(self):
        if (
            not self.end_date
            and self.start_date <= timezone.now()
            or timezone.now() > self.end_date
        ):
            return True
        return False

    def happening_now(self):
        if self.start_date <= timezone.now() <= self.end_date:
            return True
        return False

    def future(self):
        if timezone.now() < self.start_date:
            return True
        return False

    def google_calendar_link(self):
        params = {
            "action": "TEMPLATE",
            "text": self.title,
            "dates": f"{self.start_date.strftime('%Y%m%dT%H%M%S')}Z",
            "details": f"{self.description}\n\nSource: {self.source_url}",
            "location": self.location or self.organizers.first().name,
            "sf": "true",
            "output": "xml",
        }
        if self.end_date:
            params["dates"] += f"/{self.end_date.strftime('%Y%m%dT%H%M%S')}Z"
        elif self.films.first():
            end_date = self.start_date + \
                timezone.timedelta(minutes=self.films.first().runtime)
            params["dates"] += f"/{end_date.strftime('%Y%m%dT%H%M%S')}Z"
        else:
            end_date = self.start_date + timezone.timedelta(hours=1)
            params["dates"] += f"/{end_date.strftime('%Y%m%dT%H%M%S')}Z"

        urlencoded = urlencode(params)
        return "https://www.google.com/calendar/render?" + urlencoded

    def __str__(self) -> str:
        return f"{self.title}"


class Comment(models.Model):
    text = models.TextField("Comment text")
    published = models.DateField(auto_now_add=True)
    event = models.ForeignKey(
        Event, related_name="comments", on_delete=models.CASCADE)
    submitter = models.CharField(max_length=100, default="guest")


class Download(models.Model):
    title = models.CharField(max_length=2048, null=True, blank=True)
    url = models.URLField()
    size = models.IntegerField(null=True, blank=True)
    download_date = models.DateTimeField(auto_now_add=True, editable=True)
    playwright_rendered = models.BooleanField(default=False)
    content_type = models.CharField(max_length=100, null=True, blank=True)
    content = models.FileField(upload_to="downloads/", max_length=4096)
    scroll_count = models.IntegerField(null=True, blank=True)
    md5sum = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.title


class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField("Population 2005")
    fips = models.CharField("FIPS Code", max_length=2, null=True)
    iso2 = models.CharField("2 Digit ISO", max_length=2)
    iso3 = models.CharField("3 Digit ISO", max_length=3)
    un = models.IntegerField("United Nations Code")
    region = models.IntegerField("Region Code")
    subregion = models.IntegerField("Sub-Region Code")
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField()

    # Returns the string representation of the model.
    def __str__(self):
        return self.name
