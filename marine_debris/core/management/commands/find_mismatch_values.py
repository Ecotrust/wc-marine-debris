import os
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from core.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        count = 0
        mismatches = {}
        for fv in FieldValue.objects.all():
            dsf = fv.event_id.datasheet_id.datasheetfield_set.get(field_id=fv.field_id)
            key = 'dsf:%s-f:%s' % (str(dsf.id), str(fv.field_id.id))
            if not mismatches.has_key(key):
                if dsf.unit_id and fv.field_id.unit_id and not dsf.unit_id.data_type == fv.field_id.unit_id.data_type:
                    mismatches[key] = {
                        'datasheet' : dsf.sheet_id,
                        'datasheetfield': dsf,
                        'field': fv.field_id
                    }
        for key in mismatches:
            mismatch =  mismatches[key]
            print 'Value mismatch at %s: dsf %s has value %s; field has value %s' % (mismatch['datasheet'].sheetname, mismatch['datasheetfield'].field_name, mismatch['datasheetfield'].unit_id.short_name, mismatch['field'].unit_id.short_name)
                