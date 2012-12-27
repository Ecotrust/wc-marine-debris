import os
from django.core.management.base import BaseCommand, CommandError
from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        sites = [x for x in Site.objects.all()]
        for site in sites:
            if not site.sitename == site.sitename.strip() or not site.county == site.county.strip():
                conflicts = Site.objects.filter(sitename = site.sitename.strip(), county = site.county.strip())
                if conflicts.count() > 0:
                    print '"' + site.sitename + ', ' + site.county + '"'
                    good_site = conflicts[0]
                    if abs(int(site.geometry.get_coords()[1]) - int(good_site.geometry.get_coords()[1])) < 0.0001 and abs(int(site.geometry.get_coords()[0]) - int(good_site.geometry.get_coords()[0])) < 0.0001:
                        events = Event.objects.filter(site = site)
                        for event in events:
                            print 'changing event ' + str(event.id) + '\'s site from ' + str(event.site.id) + ' to ' + str(good_site.id)
                            event.site = good_site
                            event.save()
                        print 'Deleting site ' + site.sitename + ' id: ' + str(site.id)
                        site.delete()
                    else:
                        print site.sitename.strip() + ':'
                        print str(site.id) + ' and ' + str(good_site.id) + ' are a different coords!'
                        print 'Latitude: ' + str(site.geometry.get_coords()[1]) + ' | ' + str(good_site.geometry.get_coords()[1])
                        print 'Longitude: ' + str(site.geometry.get_coords()[0]) + ' | ' + str(good_site.geometry.get_coords()[0])
                else:
                    print '"' + site.sitename + ', ' + site.county + '" has no conflicts'
                    site.sitename = site.sitename.strip()
                    site.county = site.county.strip()
                    site.save()
            else:
                dupes = Site.objects.filter(sitename = site.sitename, county = site.county)
                if dupes.count() > 1:
                    master_site = dupes.order_by('id')[0]
                    for dupe in dupes:
                        if not dupe.id == master_site.id:
                            events = Event.objects.filter(site = dupe)
                            for event in events:
                                print 'changing event ' + str(event.id) + '\'s site from ' + str(event.site.id) + ' to ' + str(master_site.id)
                                event.site = master_site
                                event.save()
                            print 'Deleting dupe site ' + dupe.sitename + ' id: ' + str(dupe.id)
                            dupe.delete()