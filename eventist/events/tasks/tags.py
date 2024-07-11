from eventist.events.models import Tag, Host, Event

def find_tags_for_event(id):
    event = Event.objects.get(pk=id)
    event.tags.clear()
    print(event.title)
    for host in event.organizers.all():
        for tag in host.auto_add_tags.all():
            event.tags.add(tag)
            print(f"Added tag {tag.name} from host {host.name}")

    event.save()

def find_tags_for_all_events():
    for event in Event.objects.all():
        find_tags_for_event(event.id)
