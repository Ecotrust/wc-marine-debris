import os
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        count = 0
        mismatches = {}
        
        for ds in DataSheet.objects.all():
            for dsf in ds.datasheetfield_set.all():
                key = 'dsf:%s' % str(dsf.id)
                if not mismatches.has_key(key):
                    if dsf.unit_id and dsf.field_id.unit_id and not dsf.unit_id.data_type == dsf.field_id.unit_id.data_type:
                        mismatches[key] = {
                            'datasheet' : ds,
                            'datasheetfield': dsf,
                            'field': dsf.field_id
                        }

        for key in mismatches:
            mismatch =  mismatches[key]
            print 'Value mismatch at %s %s: \n\
            dsf %s has value %s \n\
            field has value %s\n\
            ' % (mismatch['datasheet'].created_by.orgname, mismatch['datasheet'].sheetname, mismatch['datasheetfield'].field_name, mismatch['datasheetfield'].unit_id.short_name, mismatch['field'].unit_id.short_name)
                