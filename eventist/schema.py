import graphene
from graphene_django import DjangoObjectType

from eventist.events.models import Event
from eventist.events.models import Host
from eventist.events.models import Location


class EventType(DjangoObjectType):
    class Meta:
        model = Event


class HostType(DjangoObjectType):
    class Meta:
        model = Host


class LocationType(DjangoObjectType):
    class Meta:
        model = Location


class Query(graphene.ObjectType):
    all_events = graphene.List(EventType)
    all_hosts = graphene.List(HostType)
    all_locations = graphene.List(LocationType)

    host_by_name = graphene.Field(HostType, name=graphene.String(required=True))

    def resolve_all_locations(self, info):
        return Location.objects.all()

    def resolve_all_events(self, info):
        return Event.objects.all()

    def resolve_all_hosts(self, info):
        # We can easily optimize query count in the resolve method
        return Host.objects.all()

    def resolve_host_by_name(self, info, name):
        try:
            return Host.objects.get(name=name)
        except Host.DoesNotExist:
            return None


schema = graphene.Schema(query=Query)
