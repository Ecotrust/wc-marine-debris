import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.cache import cache
from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        from core.views import download_events 
        from django.test.client import RequestFactory
            
        clear_cache = False
        try:
            if args[0].lower() == 'clear':
                clear_cache = True
        except IndexError:
            pass

        if clear_cache:
            print "Clearing event cache (with a scalpel)"
            event_ids = [x.id for x in Event.objects.all()]
            for eid in event_ids:
                # invalidate/clear all cached data associated with this event
                keys = [
                    'event_%s_eventdict' % eid,
                    'event_%s_valuedict_convert' % eid,
                ]
                for key in keys:
                    cache.delete(key)
        else:
            print "Not clearing event cache"


        for dl in Download.objects.filter(auto_generate=True):
            print dl.label

            request = RequestFactory().get(dl.url)
            eres = download_events(request)

            from django.core.files.base import ContentFile
            myfile = ContentFile(eres.content)

            dl.thefile.save(dl.filename, myfile)
