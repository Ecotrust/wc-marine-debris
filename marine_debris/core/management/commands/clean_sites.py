import os
from django.core.management.base import BaseCommand, CommandError
from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        sites = [x for x in Site.objects.all()]
        dead_list = []
        for site in sites:
            bad_sites = Site.objects.filter(sitename = site.sitename + ' ')
            if bad_sites.count() > 0:
                for site in bad_sites:
                    dead_list.append(site.id)
        print dead_list