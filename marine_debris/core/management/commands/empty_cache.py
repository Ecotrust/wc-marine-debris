import os
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        for event in Event.objects.all():
            keys = [
                    'event_%s_eventdict' % event.id,
                    'event_%s_valuedict_convert' % event.id,
                    'event_%s_valuedict_ray' % event.id,
                    'event_%s_geocache' % event.id,
                ]
            for key in keys:
                cache.delete(key)
        for field in Field.objects.all():
            cache.delete('field_%s' % field.id)

        for from_unit in Unit.objects.all():
            for to_unit in Unit.objects.all():
                cache.delete('unit_from_%s_to_%s' % (from_unit.short_name, to_unit.short_name))