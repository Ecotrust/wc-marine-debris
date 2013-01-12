import os
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        count = 0
        matches = []
        for event in Event.objects.all():
            evt_str = str(event.cleanupdate) + '-' + str(event.site) + '-' + str(event.dup)
            if not evt_str in matches:
                qs = Event.objects.filter(cleanupdate=event.cleanupdate, site=event.site, dup = event.dup)
                if qs.count() > 1:
                    matches.append(evt_str)
                    count = count + qs.count()
                    print str(qs.count()) + ' matches found for ' + evt_str