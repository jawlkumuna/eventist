from eventist.events.models import Tag, Host, Event
import re

def find_tags_for_event(id):
    event = Event.objects.get(pk=id)
    event.tags.clear()
    print(event.title)
    for host in event.organizers.all():
        for tag in host.auto_add_tags.all():
            event.tags.add(tag)
            print(f"Added tag {tag.name} from host {host.name}")

    event.save()

def refresh_all_tags():
    for event in Event.objects.all():
        find_tags_for_event(event.id)
        for tag in Tag.objects.all():
            for kw in tag.keywords.all():
                if kw.boundary:
                    if re.search(r"\b" + kw.keyword + r"\b", event.title, re.I) or \
                        re.search(r"\b" + kw.keyword + r"\b", (event.description or ""), re.I):
                        event.tags.add(tag)
                        event.save()
                        print(f"Added tag {tag.name} from keyword {kw.keyword}")
                else:
                    if kw.keyword in event.title or kw.keyword in (event.description or ""):
                        event.tags.add(tag)
                        event.save()
                        print(f"Added tag {tag.name} from keyword {kw.keyword}")
