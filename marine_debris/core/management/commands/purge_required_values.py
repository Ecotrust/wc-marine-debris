import os
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        for event in Event.objects.all():
            req_fields = settings.REQUIRED_FIELDS[event.datasheet_id.site_type].values()
            for value in event.fieldvalue_set.filter(field_id__internal_name__in=req_fields):
                print "deleting value [%s] %s for event %s" % (value.field_value, value.field_id.internal_name, event.__unicode__())
                value.delete()