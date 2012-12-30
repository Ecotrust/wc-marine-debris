import os
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        orphan_values = []
        field_values =  FieldValue.objects.all()
        for (counter, value) in enumerate(field_values):
            if counter % 1000 == 0:
                print "Value number %s of %s" % (str(counter), str(field_values.count()))
            if value.event_id:                          #FieldValue is associated with an event
                if value.event_id.datasheet_id:             #Event is associated with a datasheet
                    datasheetfield_qs = DataSheetField.objects.filter(field_id = value.field_id, sheet_id = value.event_id.datasheet_id)
                    datasheetfield_count = datasheetfield_qs.count()
                    if not datasheetfield_count == 1:        #If there is a mismatch...
                        if datasheetfield_count == 0:        #No match found
                            orphan_values.append(value)     #add orphan value to list
                        else:
                            print "Datasheet %s has multiple matches for field %s!" % (value.event_id.datasheet_id.sheetname, value.field_id.internal_name)
                            for field in datasheetfield_qs:
                                print "    %s" % field.field_name
        print "%s FieldValues were found with no DataSheetFields that match" % str(orphan_values.__len__())
        print str(orphan_values)
                        