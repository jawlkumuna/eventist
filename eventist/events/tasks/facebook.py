import hashlib
import json
import time
from datetime import datetime

import jq
import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.core.files.base import ContentFile
from playwright.sync_api import sync_playwright
from pytz import timezone

from ..models import Download
from ..models import Event
from ..models import Host
from ..models import Location
from ..admin import CookieSet


def download_facebook_page(
    url,
    scroll_amount=1000,
    scroll_count=10,
    forceDownload=False,
):
    if (
        Download.objects.filter(
            url=url, scroll_count__gte=scroll_count).exists()
        and not forceDownload
    ):
        return

    cookies = []
    for c in CookieSet.objects.first().cookies.all():
        cookies.append(
            {
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
            },
        )

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False, args=["--start-maximized"])
        ctx = browser.new_context()

        ctx.add_cookies(cookies)
        page = ctx.new_page()
        # page.on("response", lambda response: print(response.url))
        print(url)
        page.goto(url=url)
        print(page.title())
        print(page.content()[:100])
        print("scrolling")
        content = page.content()
        for i in range(scroll_count):
            page.mouse.wheel(0, scroll_amount)
            time.sleep(0.5)
        content = page.main_frame.content()

        md5sum = hashlib.md5(content.encode()).hexdigest()
        title = page.title()
    dl = Download(
        url=url,
        title=title,
        content=ContentFile(name=f"{title}.html", content=content),
        md5sum=md5sum,
        size=len(content),
        scroll_count=scroll_count,
    )
    dl.save()


@shared_task()
def find_hosts():
    A_CLASS = "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3"
    SPAN_CLASS = "x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1tu3fi x3x7a5m x1lkfr7t x1lbecb7 x1s688f xzsf02u"
    for download in Download.objects.all():
        with download.content.open() as f:
            soup = BeautifulSoup(f, "html.parser")
            for link in soup.find_all(class_=A_CLASS):
                try:
                    fbid = link["href"].split("/")[-1]
                    print(fbid, download.title)
                    name = link.find(class_=SPAN_CLASS).text
                    Host.objects.get_or_create(name=name, facebook_id=fbid)
                except Exception as e:
                    print(e)


@shared_task()
def get_events():
    A_CLASS = "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1s688f"

    for host in Host.objects.filter(starred=True):
        url = f"https://www.facebook.com/{host.facebook_id}/past_hosted_events"
        download_facebook_page.delay(url, scroll_count=50)

    for event_page in Download.objects.filter(url__contains="past_hosted_events"):
        with event_page.content.open() as f:
            soup = BeautifulSoup(f, "html.parser")
            for link in soup.find_all(class_=A_CLASS):
                try:
                    url = link["href"]
                    print(url)
                    if "events" in url:
                        title = link.find("span").text
                        Event.objects.get_or_create(
                            title=title,
                            source="facebook",
                            source_url=url,
                        )
                except Exception as e:
                    print(e)


def get_json_blocks(dlfile: Download):
    with dlfile.content.open() as f:
        soup = BeautifulSoup(f, "html.parser")
        blocks = []
        for json_block in soup.find_all("script", {"type": "application/json"}):
            try:
                data = json.loads(json_block.text)
                blocks.append(data)
            except Exception as e:
                print(e)
    return blocks


@shared_task()
def scrape_event(fbid: str, forceDownload=True):
    url = f"https://www.facebook.com/events/{fbid}"
    filt = Download.objects.filter(url__contains=url)
    if not filt.exists() or forceDownload:
        download_facebook_page(url=url, scroll_count=1,
                               forceDownload=forceDownload)
    page = filt.all().order_by("-download_date").first()
    blocks = get_json_blocks(page)
    # save blocks to file
    # with open(f"blocks_{page.title.replace('/', '|')}.json", "w") as f:
    #     json.dump(blocks, f)

    def eval_jq(query, get_all=False):
        res = jq.compile(query).input_values(blocks).all()
        if res and get_all:
            return res
        elif res:
            return res[0]
        else:
            return None

    event_name = eval_jq('.. | ."event"? |  select(.name != null).name')
    start_timestamp = eval_jq(
        '.. | ."current_start_timestamp"? |  select(. != null)')
    end_timestamp = eval_jq('.. | ."end_timestamp"? |  select(. != null)')
    # try:
    place_name = eval_jq('.. | ."event_place"? | select(. != null).name')
    lat = eval_jq('.. | ."latitude"? |  select(. != null)?')
    long = eval_jq('.. | ."longitude"? |  select(. != null)?')
    address = eval_jq('.. | ."one_line_address"? |  select(. != null)')
    description = eval_jq(
        '.. | ."event_description"? |  select(. != null) | .text')
    banner_url = eval_jq('.. | ."full_image"? |  select(. != null) | .uri?')
    going_count = eval_jq(
        '.. | ."event_connected_users_going"? | select(. != null).count',
    )
    maybe_count = eval_jq(
        '.. | ."event_connected_users_maybe"? | select(. != null).count',
    )
    hosts = eval_jq('.. | ."host"? | select(. != null)', get_all=True)
    print(
        f"{event_name}\n {start_timestamp}\n {place_name}\n {
            lat} {long}\n{going_count}\n {maybe_count}",
    )

    event, status = Event.objects.get_or_create(
        title=event_name, source_url=page.url)
    sdate = timezone("Europe/Budapest").localize(
        datetime.fromtimestamp(start_timestamp),
    )
    print(f"created status: {status}")
    event.start_date = sdate
    if end_timestamp:
        end_timestamp = timezone("Europe/Budapest").localize(
            datetime.fromtimestamp(end_timestamp),
        )
        event.end_date = end_timestamp
    event.description = description
    event.going = going_count
    event.interested = maybe_count
    if place_name:
        location, _ = Location.objects.get_or_create(
            name=place_name,
            address=address,
            latitude=lat,
            longitude=long,
        )
        event.location = location

    event.fully_scraped = True
    event.save()
    if banner_url:
        event.banner.save(
            f"{event_name}.jpg",
            ContentFile(requests.get(banner_url).content),
        )

    for host in hosts:
        # skip regular users
        if host.get("friendship_status"):
            continue
        hname = host["name"]
        print(hname)
        facebook_id = host["url"].split("/")[-1]
        past_event_count = host["past_event_count"]["count"]
        profile_picture = host["larger_profile_picture"]["uri"]
        try:
            description = host["profile_bio"]["bio"]["text"]
        except:
            description = None

        if not Host.objects.filter(facebook_id=facebook_id).exists():
            h = Host.objects.create(
                name=hname,
                facebook_id=facebook_id,
                past_event_count=past_event_count,
                profile_picture=ContentFile(
                    name=f"{hname}.jpg",
                    content=requests.get(profile_picture).content),
                description=description,
            )
            h.profile_picture.save(
                f"{hname}.jpg",
                ContentFile(requests.get(profile_picture).content),
            )

        else:
            h = Host.objects.filter(facebook_id=facebook_id)
            h.update(
                past_event_count=past_event_count,
                description=description,
            )
            if not h[0].profile_picture or h[0].profile_picture.size < 30:
                print("saving new profile picture")
                h[0].profile_picture.save(
                    f"{hname}.jpg",
                    ContentFile(requests.get(profile_picture).content),
                )
                h[0].save()
            h = h[0]
        event.organizers.add(h)
        # event[0].save()


@shared_task()
def scrape_events_by_host(hostid: str, past=False, scroll_count=15):
    A_CLASS = "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1s688f"

    if past:
        url = f"https://www.facebook.com/{hostid}/past_hosted_events"
    else:
        url = f"https://www.facebook.com/{hostid}/upcoming_hosted_events"

    if 'profile.php?' in hostid:
        if past:
            url = f"https://www.facebook.com/{hostid}&sk=past_hosted_events"
        else:
            url = f"https://www.facebook.com/{
                hostid}&sk=upcoming_hosted_events"
    download_facebook_page(url=url, scroll_count=15, forceDownload=True)
    time.sleep(1)
    filt = Download.objects.filter(url__contains=url)
    page = filt.all().order_by('-download_date').first()
    with page.content.open() as f:
        soup = BeautifulSoup(f, "html.parser")
        for link in soup.find_all(class_=A_CLASS):
            try:
                url = link["href"]
                print(url)
                if "events" in url:
                    fbid = url.split("/")[-2]
                    scrape_event.delay(fbid)
            except Exception as e:
                print(e)

@shared_task
def load_starred():
    for host in Host.objects.filter(starred=True):
        scrape_events_by_host.delay(host.facebook_id, past=False)
        time.sleep(1)
