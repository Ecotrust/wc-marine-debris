from django.core.management import setup_environ
import os
import settings
setup_environ(settings)
#==================================#
from django.contrib.gis.geos import GEOSGeometry 
from core.models import Site, State
import csv
import sys

with open(sys.argv[1], 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        pnt = GEOSGeometry('SRID=4326;POINT(%s %s)' % (row['longitude'], row['latitude']))
        state = State.objects.get(name=row['state'])
        s = Site(geometry=pnt, sitename=row['sitename'], county=row['county'], state=state)
        s.save()
        print "Site saved:", s
