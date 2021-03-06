# coding: utf-8
import settings
import itertools
import functools
from django import template
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.conf import settings
from django.http import (HttpResponseRedirect, HttpResponse, Http404,
                         HttpResponseBadRequest, HttpResponseNotFound, 
                         QueryDict)
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.views import login as default_login, logout as default_logout
from django.utils import simplejson
from django.forms.models import modelformset_factory
from django.contrib.gis.geos import Point
from django.utils.http import urlencode
from django.core.cache import cache
from django.contrib.gis.geos import Polygon, Point
from forms import *
from models import *
from sets import Set

import datetime
import time
import string
import logging
import csv
import re
from django.db.models import Max

class Timer(object):
    SECONDS = 1.0
    MILLISECONDS = 1e3
    MICROSECONDS = 1e6
    
    
    def __init__(self):
        self.start()
    
    def start(self):
        """Start (or restart) the timer. Also resets the lap counter.
        """
        self.t = datetime.datetime.now()
        self.last_lap = self.t
        self.lap_count = 0
    
    def elapsed(self, unit=SECONDS):
        """Return the elapsed time in seconds since the timer was started.
        """
        # python2.7+
        # return (datetime.datetime.now() - self.t).total_seconds() * (unit)
    
        # python <= 2.6
        diff = (datetime.datetime.now() - self.t)
        total_seconds = diff.seconds + diff.microseconds / 1e6 + (diff.days * 24 * 3600)
        total_seconds = total_seconds * unit
        return total_seconds

    def lap(self, unit=SECONDS):
        """Return the amount of time that's passed since the last call to lap. 
        Start the timer at the top of your loop, then call this in the body of 
        your loop to get the time between loop iterations.
        """
        self.lap_count += 1
        now = datetime.datetime.now()
        value, self.last_lap = (now - self.last_lap), now
        
        # return value.total_seconds() * (unit)
        
        total_seconds = value.seconds + value.microseconds / 1e6 + (value.days * 24 * 3600)
        total_seconds = total_seconds * unit
        return total_seconds
    
    def average(self, unit=SECONDS):
        """Return the average lap time
        """
        return self.elapsed(unit) / self.lap_count

    @staticmethod
    def timed_function(fn):
        """Print execution time after function completes
        """
        @functools.wraps(fn)
        def time_it(*args, **kwargs):
            t = Timer()
            try:
                result = fn(*args, **kwargs)
            except: 
                print "%s (exception) - %.2f ms" % (fn.__name__, t.elapsed(t.MILLISECONDS))
                raise
            print "%s - %.2f ms" % (fn.__name__, t.elapsed(t.MILLISECONDS))
            return result
        return time_it
    
def index(request): 
    if not settings.DEMO:
        event_count = [
            {
                "type": x.type,
                "count": Event.objects.filter(datasheet_id__type_id__type = x.type, transaction__status = "accepted").count(),
            } for x in EventType.objects.all()
        ]
    else:
        event_count = [
            {
                "type": x.type,
                "count": Event.objects.filter(datasheet_id__type_id__type = x.type).count(),
            } for x in EventType.objects.all()
        ]
    return render_to_response( 'index.html', RequestContext(request,{'thankyou': False, 'active':'home', 'event_count': event_count}))

def about(request):
    return render_to_response('about.html', RequestContext(request))
    
def resources(request):
    return render_to_response('resources.html', RequestContext(request))
  
def aggregation_info(request):
    return render_to_response('aggregation_info.html', RequestContext(request))

def fields(request):
    fields = Field.objects.all()
    
    return render_to_response('fields.html', RequestContext(request, {'fields': fields}))
    
def guidelines(request):
    return render_to_response('guidelines.html', RequestContext(request))

def terms(request):
    return render_to_response('terms.html', RequestContext(request))    
    
def get_transactions(request):
    trans_dict = {
        'new' : [trans.toDict for trans in UserTransaction.objects.filter(status='new')],
        'accepted' : [trans.toDict for trans in UserTransaction.objects.filter(status='accepted')],
        'rejected' : [trans.toDict for trans in UserTransaction.objects.filter(status='rejected')]
    }

    return HttpResponse(simplejson.dumps(trans_dict))

def management(request):
    return render_to_response( 'management.html', RequestContext(request, {'active':'management'}))

def update_transaction(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id', None)
        status = request.POST.get('status', None)
        reason = request.POST.get('reason', None)
        if settings.DEMO or settings.SERVER == 'Dev':
            send_email = False
        else:
            send_email = True
        if transaction_id is not None:
            transaction = UserTransaction.objects.get(id=transaction_id)
            original_status = str(transaction.status)
            update_transaction = True
            if status is not None:
                transaction.status = status
                if status == 'rejected':
                    if reason is not None:
                        transaction.reason = reason
                transaction.save()
                res = {'status': 'success', 'transaction_id': transaction_id}
                
                user = transaction.submitted_by
                events = Event.objects.filter(transaction=transaction)
                sites = Site.objects.filter(transaction=transaction)
                if events.count() > 0:
                    transaction_type = "events"
                    if sites.count() > 0:
                        transaction_type = "sites and " + transaction_type
                elif sites.count() > 0:
                    transaction_type = "sites"
                else:
                    send_email = False
                    
                if user.email == '' or  user.email == None:
                    send_email = False
                    update_transaction = False
                    print 'User has no email'
                    
                if send_email:
                    msg_header = "Dear %s,\n\nThis email is to inform you that the %s you created on %s have been %s.\n" %  (user.username.capitalize(), transaction_type, transaction.created_date, transaction.status)

                    if transaction.status == "rejected":
                        msg_rejected = "\nReason:\n%s\n\nIf you would still like your data included in the database, please review your data, make any recommended changes mentioned in the reason for rejection, and resubmit it.\n" % (transaction.reason)
                    else:
                        msg_rejected = ''
                        
                    msg_footer = "\nThanks again for submitting data to the West Coast Marine Debris Database. Details about your submission are below.\nTo submit more data, please visit our tool again at %s.\n\nIf you have questions, concerns, or would like to contact us for any other reason, please refer to our website (%s) for direction and information.\n\nCheers,\n- The West Coast Marine Debris Action Coordination Team Staff\n\n" % (settings.TOOL_URL, settings.WCGA_ACT_URL)
                    
                    msg_details = "\nDetails about your submitted data:\n"
                    for site in sites:
                        msg_details = msg_details + "\nSite: %s\nCounty: %s\nState: %s\n" % (site.sitename, site.county, site.state.initials)
                    for event in events:
                        msg_details = msg_details + "\nEvent Project: %s\nSite: %s\nDate: %s\n" % (event.proj_id.projname, event.site.sitename, event.cleanupdate.strftime('%m/%d/%Y'))
                    
                    message = msg_header + msg_rejected + msg_footer + msg_details

                    user.email_user("Marine Debris DB Status Update", message)
                    
                if update_transaction:
                    if status == 'rejected':
                        for event in Event.objects.filter(transaction = transaction):
                            event.delete()
                        
                    transaction.update()
                else:
                    transaction.status = original_status
                    transaction.save()
                    res = {
                        'status_code': 400,
                        'status': 'failed',
                        'error':  'User %s has no email address. Assign one in the administration tool before changing transaction status.' % transaction.submitted_by.username
                    }
    else:
        res = {
            'status_code': 400,
            'status': 'failed',
            'error':  'request was not a POST'
        }
    return HttpResponse(simplejson.dumps(res))
    
def events(request, submit=False): 
    
    if settings.SERVER == 'Dev':
        static_media_url = settings.MEDIA_URL
    else:
        static_media_url = settings.STATIC_URL

    if submit:
        return render_to_response( 'events.html', RequestContext(request,{'submit':True, 'added_site':submit, 'active':'events', 'STATIC_URL':static_media_url}))
    else:
        return render_to_response( 'events.html', RequestContext(request,{'submit':submit, 'added_site':None, 'active':'events', 'STATIC_URL':static_media_url}))
        
def get_filters(request):
    states = []
    locations = {}
    organizations = []
    projects = []
    fields = []
    for state in State.objects.all().order_by('name'):
        states.append(state.toSimpleDict)
        counties = []
        for county in County.objects.filter(stateabr=state.initials).order_by('name'):
            counties.append({
                "name": county.name,
                "type": 'county',
                "state": state.name
            })
        locations[state.name] = {
            'counties' : counties,
            'state' : state.name,
        }
    for organization in Organization.objects.all():
        organizations.append({
            "name": organization.orgname,
            "id": organization.id,
            "slug": organization.slug
        })
    for project in Project.objects.all():
        projects.append({
            "name": project.projname,
            "id": project.id,
            "slug": project.slug
        })

    for field in Field.objects.all():
        fields.append({
            "name": field.label,
            "slug": field.internal_name,
            "id": field.id
        })

    return HttpResponse(simplejson.dumps({
        'states': states,
        'locations': locations,
        "projects": projects,
        "organizations": organizations,
        "fields": fields
    }))


def download_stream_generator(request):
    yield ' ' # yield something immediately to start the download
    filter_json = request.GET.get('filter', False)
    pretty_headers = request.GET.get('pprint', False)

    if filter_json:
        filters = simplejson.loads(filter_json)
        qs = Event.filter(filters)
    else:
        filters = None
        qs = Event.objects.all()

    if not settings.DEMO:
        qs = qs.filter(transaction__status = "accepted")
        
    data = []
    all_fieldnames = Set([])
    for event in qs: 
        print event.id, event
        d = event.toEventsDict
        evd = event.toValuesDict()
        d['field_values'] = evd
        all_fieldnames = Set(evd.keys()) | all_fieldnames
        # data.append(d)

    ordered_fieldnames = list(all_fieldnames)
    ordered_fieldnames.sort()
    header = [
            'id', 
            'date',
            'project_name',
            'site_name',
            'site_state',
            'site_county',
            'site_lon',
            'site_lat',
            'event_type',
            'datasheet',
            'organization',
    ]

    if pretty_headers:
        header = [x.replace('_',' ').title() for x in header]
        for x in ordered_fieldnames:
            clean_head = re.sub(r',', '', x[1])
            if x[2]: # if units are defined
                header.append("%s (%s)" % (clean_head, x[2]))
            else:
                header.append("%s" % clean_head)
    else:
        header.extend([x[0] for x in ordered_fieldnames])

    row = ','.join(header)
    row += "\n"
    yield row

    # for d in data:
    for event in qs: 
        d = event.toEventsDict
        evd = event.toValuesDict()
        d['field_values'] = evd
        row_data = [
                d['id'],
                d['date'],
                d['project']['name'],
                d['site']['name'],
                d['site']['state'],
                d['site']['county'],
                d['site']['lon'],
                d['site']['lat'],
                d['datasheet']['event_type'],
                d['datasheet']['name'],
                d['organization']['name'],
        ]
        for fname in ordered_fieldnames:
            try:
                v = d['field_values'][fname]
            except KeyError:
                v = ''
            if v is None:
                v = ''
            row_data.append(v)

        row = ','.join(('"%s"' % x for x in row_data))
        row += "\n"
        yield row

def download_events(request):
    print "download events"
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = request.GET.get('filename', 'WCGA_debris_%s' % timestamp )
    res = HttpResponse(download_stream_generator(request), content_type="text/csv")
    res['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename
    print "download events returns"
    return res

event_sort_cols = {
    "site.st_initials": 'site__state',
    "datasheet.event_type": "datasheet_id__type_id",
    "site.name": "site__sitename",
    "site.county": "site__county",
    "date": "cleanupdate"
}

def get_events(request):
    start_index = request.GET.get('iDisplayStart', 0)
    count = request.GET.get('iDisplayLength', False)
    sEcho = request.GET.get('sEcho', False)
    sort_column = request.GET.get('iSortCol_0', False)
    filter_json = request.GET.get('filter', False)
    start_id = request.GET.get('startID', False)
    accepted_only = request.GET.get('accepted-only', False)
    
    if settings.DEMO:
        accepted_only = False

    if filter_json:
        filters = simplejson.loads(filter_json)
        qs = Event.filter(filters)
    else:
        filters = []
        qs = Event.objects.all()

    if accepted_only:
        qs = qs.filter(transaction__status = "accepted")
    
    if sort_column:
        sort_name_key = request.GET.get("mDataProp_%s" % sort_column, False)
        sort_dir = request.GET.get("sSortDir_0", False)
        if sort_name_key:
            sort_name = event_sort_cols[sort_name_key]
            if sort_dir == 'desc':
                sort_name = "-" + sort_name
            qs = qs.order_by(sort_name)
    for filter in filters:
        if filter['type'] == 'point':    
            coords = filter['value'].split(':')
            point = Point(float(coords[0]), float(coords[1]))
            qs = qs.distance(point, field_name='site__geometry').order_by('distance')
    filtered_count = qs.count()
    if count and not start_id:
        qs = qs[int(start_index):int(start_index) + int(count)]

    data = []
    found_records = 0

    for event in qs: 
        dict = event.toEventsDict
        if not start_id:
            data.append(dict)
        else:
            # if we do have a startid (because we clicked on a map point)
            # loop thorugh the sorted filtered list and grap the records from
            # the clicked event, up to count
            if found_records > int(count):
                break
            if event.id == int(start_id):
                data.append(dict)
                found_records = 1
            elif found_records >= 1 and found_records < int(count):
                data.append(dict)
                found_records = found_records + 1
            
    if accepted_only:
        total_records = Event.objects.filter(transaction__status = "accepted")
    else:
        total_records = Event.objects.all()
    
    res = {
       "aaData": data,
       "iTotalRecords": total_records.count(),
       "iTotalDisplayRecords": filtered_count,
       "sEcho": sEcho
    }
    return HttpResponse(simplejson.dumps(res))

site_sort_cols = {
    'name': "sitename",
    'state': 'state',
    'county': 'county'
}

    
def get_sites(request):
    start_index = request.GET.get('iDisplayStart', 0)
    count = request.GET.get('iDisplayLength', False)
    sEcho = request.GET.get('sEcho', False)
    sort_column = request.GET.get('iSortCol_0', False)
    transaction = request.GET.get('transaction', False)
    start_id = request.GET.get('startID', False)

    if transaction:
        qs = Site.objects.filter(transaction__id=transaction)
        if sort_column:
            sort_name_key = request.GET.get("mDataProp_%s" % sort_column, False)
            sort_dir = request.GET.get("sSortDir_0", False)
            if sort_name_key:
                sort_name = site_sort_cols[sort_name_key]
                if sort_dir == 'desc':
                    sort_name = "-" + sort_name
                qs = qs.order_by(sort_name)
        filtered_count = qs.count()
        if count and not start_id:
            qs = qs[int(start_index):int(start_index) + int(count)]
    else:
        filtered_count = qs.count()
        qs = Site.objects.all()

    data = []

    for site in qs: 
        dict = site.toDict
        data.append(dict)
            
    res = {
       "aaData": data,
       "iTotalRecords": Site.objects.all().count(),
       "iTotalDisplayRecords": filtered_count,
       "sEcho": sEcho
    }
    return HttpResponse(simplejson.dumps(res))

def srid_to_proj(srid):
    """
    Take a postgis srid and return the proj4 string
    Useful for custom projections with no authority
    """
    from django.contrib.gis.gdal import SpatialReference
    srs = SpatialReference(srid)
    return srs.proj.strip()
    
def get_feature_json(geom_json, prop_json):
    return """{
        "type": "Feature",
        "geometry": %s,
        "properties": %s
    }""" % (geom_json, prop_json)    


def event_search(request):
    t = Timer()

    query = EventOntology.objects.all()
   
    # Each category is a list of concepts (internal_name) that belong together 
    # in some externally defined grouping.
    # When the searcher passes a category, they want any Event that has any 
    # of the selected concepts with counts > 0. 
    # When the searcher passes a concept in addition to a category, they also 
    # get any Events containing the single concept with counts > 0
    #   
    # So, if "category" is {A, B, C}, searching for that category will return 
    # counts for any of those that have values > 0; if you add a concept {D}, 
    # then you'll get counts of any of A, B, C + counts of D. 
    
    # It looks like this kind of search reduces to concepts occuring in a list
    # or individually

    search_groups = request.GET.getlist('c')
    if search_groups:
        search_groups = [x.split(',') for x in search_groups]
        # flatten (see: http://stackoverflow.com/a/952952/65295)
        search_groups = [item for sublist in search_groups
                              for item in sublist]
    
        query = query.filter(internal_name__in=search_groups)


    format_ = request.GET.get('format', 'text') # either format=json or you get text
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    type_ = request.GET.get('type') # TODO: Make type required, since behavior depends on this

    # construct the query based on the type. 
    # Derelict Gear Removal *only* returns the fields used to construct this
    # particular response. Also, the 'count' for DG is always 1.  
    # Site Cleanups are more general. 

    if type_ == 'Derelict Gear Removal':
        # The manager on EventSearchDerelictGear only knows "fetch", and knows
        # how to handle the date range. 
        query = EventSearchDerelictGear.objects.fetch(date_from, date_to)
    else:
        query = query.filter(type='Site Cleanup')
    
        if date_from:
            query = query.filter(cleanupdate__gte=date_from)
        
        if date_to:
            query = query.filter(cleanupdate__lte=date_to)
    
        query = query.filter(field_value_float__gt=0)
    
    if format_ == 'json':
        srid = settings.GEOJSON_SRID
        crs = srid_to_proj(srid)
        
        # Generating the JSON directly is much faster than assembling data in
        # python, and then serializing to JSON. It's a bit harder to read though
        feature_collection = """{
    "type": "FeatureCollection",
    "crs": { "type": "name", "properties": {"name": "%s"}},
    "features": [%s]
}"""
        features = []
        for row in query: 
            feature = """    {
        "type": "Feature",
        "geometry": %(geometry)s,
        "properties": {
            "id": "%(field_value_id)s",
            "count": %(field_value_float)d,
            "field_value": "%(field_value)s",
            "internal_name": "%(internal_name)s",
            "unit": "%(unit)s",
            "event_type": "%(type)s",
            "date": "%(date)s",
            "displayName": "%(sitename)s / %(date)s",
            "event_id": %(event_id)d
        }
    }""" % dict(field_value_id=row.field_value_id,
                field_value=row.field_value, # only useful in DG queries
                field_value_float=int(row.field_value_float), # data type is float, but data is int 
                internal_name=row.internal_name,
                geometry=row.geometry,
                type=row.type,
                unit=row.unit,
                date=row.cleanupdate.strftime('%m/%d/%Y'),
                sitename=row.sitename.replace('"', '\\"'),
                event_id=getattr(row, 'event_id', -1))
            
            features.append(feature)
        
        feature_collection = feature_collection % (crs, ',\n'.join(features))

#         print "Data generation time", t.lap()
#         print "JSON Encoding time", t.lap()
        r = HttpResponse(feature_collection, mimetype='application/json')
    else: 
        out = [','.join((str(item.cleanupdate), item.internal_name, item.field_value)) 
               for item in query]
        out = '\n'.join(out)
        r = HttpResponse(out, mimetype='text/plain')
        
    return r

def get_event_geojson(request):
    t = Timer()
    
    srid = settings.GEOJSON_SRID
    crs = srid_to_proj(srid)
    filter_json = request.GET.get('filter', False)
    bbox = request.GET.get('bbox', False)
    
    if filter_json and bbox:
        qs = Event.filter(simplejson.loads(filter_json), simplejson.loads(bbox))
    elif filter_json:
        qs = Event.filter(simplejson.loads(filter_json))
    else:
        qs = Event.objects.all()
    
    if not settings.DEMO:
        qs = qs.filter(transaction__status = "accepted")
    
    print "Load filter time", t.lap()
    
    feature_jsons = []
    for event in qs:
        key = 'event_%s_geocache' % event.id        #CACHE_KEY  --  geojson by event
        geo_string = cache.get(key)
        if not geo_string:
            gj = None
            try:
                gj = event.site.geometry.geojson
                properties = simplejson.dumps({
                    "id":event.id,
                    "event_type": event.datasheet_id.type_id.type,
                    "date": event.cleanupdate.strftime('%m/%d/%Y'),
                    "displayName": "%s / %s" % (event.site.sitename, event.cleanupdate.strftime('%m/%d/%Y'))
                })
            except AttributeError:
                pass
             
            geo_string = get_feature_json(gj, properties)
            cached = cache.set(key, geo_string, settings.CACHE_TIMEOUT)
            
        feature_jsons.append(geo_string)
    print "Time to complete loop", t.lap()
    
    geojson = """{
        "type": "FeatureCollection",
        "crs": { "type": "name", "properties": {"name": "%s"}},
        "features": [
            %s
        ]
    }""" % (crs, ', \n'.join(feature_jsons),)
    
    response = HttpResponse()
    response['Content-Type'] = 'application/json'
    response.write(geojson)
    return response
        
def get_aggregate_values_list(request, filters=None):
    '''
    TODO profile
    '''
    cleanup_events = Event.filter(filters)
    if not settings.DEMO:
        cleanup_events = cleanup_events.filter(transaction__status = "accepted")
        
    agg_fields = {}

    event_values_list = [x.toValuesDict() for x in cleanup_events]
    field_values = []
    datasheets = []
    categories = {}
    display_categories={}

    for event in cleanup_events:
        datasheet = event.toEventsDict['datasheet']
        if not display_categories.has_key(str(datasheet['id'])):
            new_datasheet = True
            display_categories[str(datasheet['id'])] = {}
        else:
            new_datasheet = False
        if datasheet['name'] not in datasheets:
            datasheets.append(datasheet['name'])
        for dsf in datasheet['datasheetfields']:
            if dsf['field']['datatype']['aggregatable']:
                if not agg_fields.has_key(dsf['field']['name']):
                    agg_fields[dsf['field']['name']] = get_agg_template(dsf['field'])
                agg_fields[dsf['field']['name']]['num_values'] = agg_fields[dsf['field']['name']]['num_values'] + 1
                if dsf['field'].has_key('display_category') and dsf['field']['display_category']['name'] not in ['Location', 'Date', 'Event', 'Debris', 'Mixed', '']:
                    display_category = dsf['field']['display_category']['name']
                    if not categories.has_key(display_category):
                        print "adding cat key %s" % display_category
                        categories[display_category] = {
                            'pounds': {
                                'total': 0,
                                'ds_hits': 0
                            },
                            'count': {
                                'total': 0,
                                'ds_hits': 0
                            }
                        }
                    if new_datasheet:
                        if not display_categories[str(datasheet['id'])].has_key(display_category):
                            display_categories[str(datasheet['id'])][display_category] = {
                                'pounds': False,
                                'count': False
                            }
                        if dsf['field']['datatype']['name'] == 'Weight':
                            display_categories[str(datasheet['id'])][display_category]['pounds'] = True
                        if dsf['field']['unit']['short_name'] == 'Count':
                            display_categories[str(datasheet['id'])][display_category]['count'] = True
        for key in categories.keys():
            if display_categories[str(datasheet['id'])].has_key(key):
                print "datasheet has key %s" % key
                if display_categories[str(datasheet['id'])][key]['pounds']:
                    categories[key]['pounds']['ds_hits'] = categories[key]['pounds']['ds_hits'] + 1
                if display_categories[str(datasheet['id'])][key]['count']:
                    categories[key]['count']['ds_hits'] = categories[key]['count']['ds_hits'] + 1
            
    fields = Field.toFieldsDict()
            
    for event_value in event_values_list:
        field_values.extend([{'int_name':x[0], 'label':x[1], 'value':event_value[x]} for x in event_value])

    for field_value in field_values:
        
        db_field = fields[field_value['int_name']]
        if db_field['datatype']['aggregatable']:
            #sum up values for table
            if (field_value['value'] or field_value['value'] == 0) and not field_value['value'] in ['', None, 'None']:
                if not agg_fields.has_key(field_value['int_name']):
                    agg_fields[field_value['int_name']] = get_agg_template(db_field)
                field = agg_fields[field_value['int_name']]
                
                if not field['value']:
                    field['value'] = 0

                field['value'] = field['value'] + float(field_value['value'])
                #Collect data for high-level categories
                if db_field['display_category']['name'] not in ['Location', 'Date', 'Event', 'Debris', 'Mixed', ''] and (db_field['unit']['short_name'] == 'Count' or db_field['datatype']['name'] == 'Weight'):
                    if not categories.has_key(db_field['display_category']['name']):        #This should only happen if a FieldValue is no longer related to a DataSheetField (the DataSheet was changed after data was entered)
                        categories[db_field['display_category']['name']] = {
                            'pounds': {
                                'total': 0,
                                'ds_hits': 0
                            },
                            'count': {
                                'total': 0,
                                'ds_hits': 0
                            }
                        }
                    if db_field['datatype']['name'] == 'Weight':
                        if not db_field['unit']['slug'] == 'pounds_lbs':
                            factor = Unit.get_conversion_factor(db_field['unit']['slug'],'pounds_lbs')
                            lbs_val = factor * field_value['value']
                        else:
                            lbs_val = field_value['value']
                        categories[db_field['display_category']['name']]['pounds']['total'] = categories[db_field['display_category']['name']]['pounds']['total'] + float(lbs_val)
                    else:
                        categories[db_field['display_category']['name']]['count']['total'] = categories[db_field['display_category']['name']]['count']['total'] + float(field_value['value'])
                        
    field_list = []

    for agg_field in agg_fields:
        field_list.append(agg_fields[agg_field])
        
    category_list = []
    for category in categories:
        category_list.append({
            'name': category,
            'pounds': categories[category]['pounds'],
            'count': categories[category]['count']
        })

    ret_dict = {
        'report':{
            'events': event_values_list.__len__(),
            'datasheets': datasheets,
            'categories': category_list
        },
        'fields': field_list
    }
        
    return ret_dict
    
def get_agg_template(field):
    if field['unit']:
        unit = field['unit']['short_name']
    else:
        unit = ''
    return {
        'name': field['name'],
        'label': field['label'],
        'type': field['datatype']['name'],
        'unit': unit,
        'value': None,
        'num_values': 0
    }
    
def get_event_values(request):
    filters = request.GET.get('filters', None)
    if filters:
        filters = simplejson.loads(filters)
    field_list = get_aggregate_values_list(request, filters)
    return HttpResponse(simplejson.dumps(field_list))
    
@login_required
def create_event(request):
    error = None
    status_code = 200
    if request.method == 'GET':
        form = CreateEventForm()

    else :
        eventForm = CreateEventForm
        form = eventForm(request.POST)

        form.validate_event()
        if form.is_valid():
            form.fields['organization'].widget = form.fields['organization'].hidden_widget()
            form.fields['project'].widget = form.fields['project'].hidden_widget()
            form.fields['date'].widget = form.fields['date'].hidden_widget()
            form.fields['data_sheet'].widget = form.fields['data_sheet'].hidden_widget()
            event = {}
            
            event['organization'] = form.data['organization']
            event['project'] = form.data['project']
            event['date'] = form.data['date']
            datasheet = DataSheet.objects.get(id=form.data['data_sheet'])
            event['data_sheet'] = datasheet.sheetname
            
            if datasheet.type_id:
                derelict = not datasheet.type_id.display_sites
            else:
                derelict = False
            if derelict:
                form.fields['sitename'].widget = form.fields['sitename'].hidden_widget()
                form.fields['county'].widget = form.fields['county'].hidden_widget()
            
            state_dict = [state.toDict for state in State.objects.all()]
            state_json = simplejson.dumps(state_dict)
            
            return render_to_response('event_location.html', RequestContext(request, {'form':form.as_p(), 'states': state_json, 'event': event, 'derelict': derelict, 'active':'events'}))
        else:
            error = 'Form is not valid, please review.'
            status_code = 400
        
    form.fields['state'].widget = form.fields['state'].hidden_widget()
    form.fields['county'].widget = form.fields['county'].hidden_widget()
    form.fields['sitename'].widget = form.fields['sitename'].hidden_widget()
    form.fields['latitude'].widget = form.fields['latitude'].hidden_widget()
    form.fields['longitude'].widget = form.fields['longitude'].hidden_widget()

    org_dict = [org.toDict for org in Organization.objects.filter(users=request.user)]
    org_json = simplejson.dumps(org_dict)

    res = render_to_response('create_event.html', RequestContext(request,{'form':form.as_p(), 'json':org_json, 'error': error, 'active':'events'}))
    res.status_code = status_code
    return res

@login_required            
def event_location(request, form=None):
    createEventForm = CreateEventForm
    eventForm = createEventForm(request.POST)
    event = {}
    event['organization'] = eventForm.data['organization']
    event['project'] = eventForm.data['project']
    event['date'] = eventForm.data['date']
    datasheet = DataSheet.objects.get(id=eventForm.data['data_sheet'])
    event['data_sheet'] = datasheet.sheetname
    site_check = eventForm.validate_site()
    unique_check = eventForm.validate_unique()
    
    if eventForm.is_valid() and site_check['valid'] and unique_check['valid']:        #TODO: Manage new sites here!
        for item in eventForm.fields.items():
            eventForm.fields[item[0]].widget = eventForm.fields[item[0]].hidden_widget()
        datasheet_id = eventForm.data['data_sheet']
        datasheet = DataSheet.objects.get(id=datasheet_id)
        if datasheet.type_id and datasheet.type_id.display_sites:
            event['sitename'] = eventForm.data['sitename']
            event['county'] = eventForm.data['county']
        event['state'] = eventForm.data['state']
        event['latitude'] = eventForm.data['latitude']
        event['longitude'] = eventForm.data['longitude']
        if form:
            formError = "Please correct the errors in your form below."
            form.hideRequiredFields(datasheet)
        else:
            formError = None
            form = DataSheetForm(datasheet, None, request.POST)
        
        return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p(), 'eventForm': eventForm.as_p(), 'event':event, 'active':'events', 'error':formError}))
    else :
    
        error = 'There is an error in your location data. Please be sure to fill out all required fields.'
        if not site_check['valid'] and not site_check['error'] == '':
            error = site_check['error']
        elif not unique_check['valid'] and not unique_check['error'] == '':
            error = unique_check['error']
    
        eventForm.fields['organization'].widget = eventForm.fields['organization'].hidden_widget()
        eventForm.fields['project'].widget = eventForm.fields['project'].hidden_widget()
        eventForm.fields['date'].widget = eventForm.fields['date'].hidden_widget()
        eventForm.fields['data_sheet'].widget = eventForm.fields['data_sheet'].hidden_widget()
        if not datasheet.type_id.display_sites:
            eventForm.fields['county'].widget = eventForm.fields['county'].hidden_widget()
            eventForm.fields['sitename'].widget = eventForm.fields['sitename'].hidden_widget()
        
        state_dict = [state.toDict for state in State.objects.all()]
        state_json = simplejson.dumps(state_dict)
        
        return render_to_response('event_location.html', RequestContext(request, {'form': eventForm.as_p(), 'states': state_json, 'event':event, 'active': 'events', 'error': error }))

@login_required
def event_save(request):
    createEventForm = CreateEventForm(request.POST)
    if createEventForm.is_valid():
        organization = Organization.objects.get(orgname=createEventForm.data['organization'])
        project = Project.objects.get(projname=createEventForm.data['project'])
        datasheet = DataSheet.objects.get(id=createEventForm.data['data_sheet'])
        state = State.objects.get(initials=createEventForm.data['state'])
        point = Point(float(createEventForm.data['longitude']), float(createEventForm.data['latitude']))
        
        user_transaction = UserTransaction(submitted_by = request.user, status='new', organization=organization, project=project)
        user_transaction.save()
        if user_transaction.id:
            if datasheet.type_id.display_sites:        
                sitename = createEventForm.data['sitename']
            else:
                sitename = "%s, %s" % (createEventForm.data['longitude'], createEventForm.data['latitude'])

            if createEventForm.data['county'] == '':
                site, created = Site.objects.get_or_create(state = state, geometry = str(point), sitename = sitename)
            else:
                county = createEventForm.data['county']
                if Site.objects.filter(state=state, county=county, geometry = str(point), sitename = sitename).count() == 0:
                    if Site.objects.filter(state=state, county=county+' County', geometry = str(point), sitename = sitename).count() > 0:
                        county = county + ' County'
                site, created = Site.objects.get_or_create(state = state, county = county, geometry = str(point), sitename = sitename)
            
            if created:
                site.transaction = user_transaction
                site.save()
            
            date = datetime.datetime.strptime(createEventForm.data['date'], '%m/%d/%Y')
            event = Event(proj_id = project, datasheet_id = datasheet, cleanupdate = date, site = site, transaction = user_transaction)
            event.save()
            if event.id:
                datasheetForm = DataSheetForm(event.datasheet_id, event, None, request.POST)
            if event.id and datasheetForm.is_valid():
                datasheetForm.save(datasheet)
                return HttpResponseRedirect('/events/%s' % event.id)
            else:
                Event.delete(event)
                if created:
                    Site.delete(site)
                return event_location(request, datasheetForm)
        else:
            UserTransaction.delete(user_transaction)
            event = {}
            event['organization'] = createEventForm.data['organization']
            event['project'] = createEventForm.data['project']
            event['date'] = createEventForm.data['date']
            event['data_sheet'] = createEventForm.data['data_sheet']
            event['state'] = createEventForm.data['state']
            event['county'] = createEventForm.data['county']
            event['sitename'] = createEventForm.data['sitename']
            event['latitude'] = createEventForm.data['latitude']
            event['longitude'] = createEventForm.data['longitude']
            return render_to_response('fill_datasheet.html', RequestContext(request, {'form':datasheetForm.as_p(), 'eventForm': createEventForm.as_p(), 'error':'Form is not valid, please review.', 'event': event}))
    else:
        return render_to_response('create_event.html', RequestContext(request, {'form':createEventForm.as_p(), 'active':'events'}))

@login_required    
def edit_event(request, event_id):
    event = Event.objects.get(id=event_id)
    eventForm = EventForm
    if request.method == 'GET':
        form = eventForm(instance=event)
    else:
        old_datasheet_id = event.datasheet_id.id
        form = eventForm(request.POST, instance=event)
        if form.is_valid():
            if int(form.data['datasheet_id']) == old_datasheet_id:
                form.save()
            else:
                FieldValue.objects.filter(event_id=event).delete()
                form.save()
                #TODO: make this land somewhere useful - used to go to create/data
                return HttpResponseRedirect('/event/create/')
            return HttpResponseRedirect('/events')
        else:
            return render_to_response( 'edit_event.html', RequestContext(request,{'event':event, 'form':form.as_p(), 'error':'Form is not valid, please review.', 'active':'events'}))
    return render_to_response( 'edit_event.html', RequestContext(request,{'event':event, 'form':form.as_p(), 'active':'events'}))
    
def view_event(request, event_id):
    event = Event.objects.get(id=event_id)
    field_list = event.field_values_list
    fields = simplejson.dumps({
        "fields": field_list,
        "details": event.toEventsDict
    })

    return HttpResponse(fields, mimetype='application/json')
    
@login_required
def delete_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.GET.has_key('delete'):
        event.delete()
        return HttpResponseRedirect('/events')
    if request.GET.has_key('cancel'):
        return HttpResponseRedirect('/events')
    values = FieldValue.objects.filter(event_id=event_id)
    fields = []
    for value in values:
        field_name = Field.objects.get(id=value.field_id.id).internal_name
        field = (field_name, value.field_value)
        fields.append(field)
    return render_to_response('delete_event.html', RequestContext(request,{'event':event, 'fields':fields, 'active':'events'}))

# @login_required
def datasheets(request):
    sheets1 = DataSheet.objects.all().order_by('-year_started', 'created_by', 'sheetname')
    sheets = []
    sheets_null = []
    for sheet in sheets1:
        if sheet.year_started:
            sheets.append(sheet)
        else:
            sheets_null.append(sheet)
        
    sheets = sheets + sheets_null
    return render_to_response('datasheets.html', RequestContext(request, {'sheets':sheets, 'active':'datasheets'}))
    
@login_required
def edit_datasheet(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'GET':
        form = DataSheetForm(event.datasheet_id, event, None)
        event_details = {
            'organization': event.proj_id.projectorganization_set.get(is_lead=True).organization_id.orgname,
            'project': event.proj_id.projname,
            'date': event.cleanupdate.strftime('%m/%d/%Y'),
            'data_sheet': event.datasheet_id.sheetname,
            'state': event.site.state.name,
            'latitude': event.site.lat,
            'longitude': event.site.lon
        }
        if event.datasheet_id.type_id.display_sites:
            event_details['county'] = event.site.county
            event_details['sitename'] = event.site.sitename
        return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p(), 'eventForm': None, 'event': event_details, 'action': '/datasheet/edit/'+str(event_id), 'active': 'events'}))
    else:
        datasheetForm = DataSheetForm
        form = datasheetForm(event.datasheet_id, event, None, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/events/True')
        else:
            event_details = {
            'organization': event.proj_id.projectorganization_set.get(is_lead=True).organization_id.orgname,
            'project': event.proj_id.projname,
            'date': event.cleanupdate.strftime('%m/%d/%Y'),
            'data_sheet': event.datasheet_id.sheetname,
            'state': event.site.state.name,
            'latitude': event.site.lat,
            'longitude': event.site.lon
        }
        if event.datasheet_id.type_id.display_sites:
            event_details['county'] = event.site.county
            event_details['sitename'] = event.site.sitename
        return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p(), 'eventForm': None, 'event': event_details, 'action': '/datasheet/edit/'+str(event.event_id), 'active': 'events', 'error':'Some answers were invalid. Please review them.'}))

def view_datasheet(request, sheet_slug):
    sheet = DataSheet.objects.get(slug=sheet_slug)
    sheet.fields = sheet.datasheetfield_set.all()
    
    return render_to_response('sheet-detail.html', RequestContext(request, {'sheet': sheet}))

# @login_required
def organizations(request): 
    organizations = []
    for organization in Organization.objects.all().order_by('orgname'): 
        organization.projects = Project.objects.filter(organization = organization)
        organizations.append(organization)

        
    return render_to_response( 'organizations.html', RequestContext(request,{'organizations':organizations, 'active':'organizations'}))

def view_organization(request, organization_slug):
    organization = Organization.objects.get(slug=organization_slug)
    organization.projects = Project.objects.filter(organization = organization)
    
    return render_to_response('organization-detail.html', RequestContext(request, {'organization': organization}))

def view_project(request, project_slug):
    project = Project.objects.get(slug=project_slug)
    project.organizations = project.organization.filter(projectorganization__is_lead=True)
    project.data_sheets = project.active_sheets.all()
    print project
    
    return render_to_response('project-detail.html', RequestContext(request, {'project': project}))

# @login_required
def projects(request): 
    projects = Project.objects.all()       
    
    return render_to_response( 'projects.html', RequestContext(request,{'projects': projects, 'active':'projects'}))    

def map_test(request):
    return render_to_response('map-test.html', RequestContext(request, {}))

def bulk_csv_header(request, datasheet_id):
    ds = DataSheet.objects.get(id=datasheet_id)
    field_names = ds.fieldnames()
    header = ','.join(["\"%s\"" % f for f in field_names])
    test_row = '' #TODO put valid default values?
    filename = slugify(ds.sheetname) + ".csv"
    response = HttpResponse('\n'.join([header, test_row]) , mimetype="text/csv")
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

def bulk_bad_request(form, request, errors=None, site_form=None, json=None):
    if not errors:
        errors = []
    if not json:
        org_dict = [org.toDict for org in Organization.objects.all()]
        json = simplejson.dumps(org_dict)
    res = render_to_response('bulk_import.html', 
            RequestContext(request,{'form':form.as_p(), 'site_form': site_form, 
                'errors':errors, 'active':'events', 'json': json, 'active':'events'}))
    res.status_code = 400
    return res

################# Utilities
class LatLonError(Exception):
    pass

def get_required_val(ds, key, row):
    """
    For a site_type and required field key, find the row's current value
    ex: for site-based event types, find the current row's `sitename`
    """
    sheet_global_required_fields = ds._required_global_field_names()
    field_name = sheet_global_required_fields[key]['field_name']
    return row[field_name]

def get_state(statename):
    statename = statename.strip()

    try:
        state = State.objects.get(name__iexact=statename)
    except State.DoesNotExist:
        state = State.objects.get(initials__iexact=statename)
        # TODO: Handle the other DoesNotExist exception here, or make sure 
        # that it's propogated correctly in the caller. 
    return state

def get_site_key(ds, row):
    if ds.site_based:
        site_key = {
            'sitename': get_required_val(ds, 'sitename', row),
            'state': get_state(get_required_val(ds,'state', row)),
            'county': get_required_val(ds,'county', row),
        }
    else:
        try:
            site_key = {
                'geometry': 'POINT(%f %f)' % (float(get_required_val(ds,'longitude', row)), float(get_required_val(ds,'latitude', row))),
            }
        except ValueError:
            raise LatLonError()

    return site_key

def get_querydict(ds, row):
    row_qnum = {} # keys must refer to the question number (ie 'question_768') 
    #field_id_lookup = dict([(f.field_name, f.id) for f in ds.datasheetfield_set.all()])
    field_id_lookup = dict(result for result in ds.datasheetfield_set.values_list('field_name', 'id'))

    for k,v in row.items():
        dsfid = field_id_lookup[k]
        row_qnum['question_%d' % dsfid] = v

    qd = QueryDict('')
    qd = qd.copy() # to make it mutable
    qd.update(row_qnum)
    return qd
                    
def parse_date(date_string):
    accepted_formats = [
        "%m/%d/%Y",
        "%Y-%m-%d",
    ]
    d = None
    for f in accepted_formats:
        try:
            d = datetime.datetime.strptime(date_string,f)
            break
        except ValueError:
            continue

    if not d:
        raise ValueError("Cannot parse date string '%s'" % date_string)

    return d


@login_required    
def bulk_import_old(request):
    org_dict = [org.toDict for org in Organization.objects.all()]
    org_json = simplejson.dumps(org_dict)
    print org_json
    if request.method == 'GET':
        form = BulkImportForm() # instance=ds)
    else: 
        return bulk_import_post(request, org_json)
    
    return render_to_response('bulk_import.html', 
                              RequestContext(request, {'form':form.as_p(), 
                                                       'json':org_json,
                                                       'active':'events'}))

def yield_some(iterable, howmany): 
    """Helper generator to get a handful of things from an iterable"""
    count = 0
    for i in iterable:
        if count >= howmany: 
            return
        count += 1
        yield i

@login_required
def bulk_import(request):
    bulk = BulkImportHandler(request)
    return bulk.dispatch()

class BulkImportHandler(object):
    """Class-based handler for bulk_import.
    """
    def __init__(self, request):
        self.request = request
        self.logger = logging.getLogger('bulk_import')
        self.response = None
        self.errors = [] # common collection to store response error messages

    def dispatch(self):
        if self.request.method == 'GET':
            self.handle_get()
        else: # post
            self.handle_post()

        return self.response

    def handle_get(self):
        org_json = self.get_org_json()
        rc = RequestContext(self.request, {'form': BulkImportForm().as_p(),
                                           'json': org_json,
                                           'active': 'events'})
        self.response = render_to_response('bulk_import.html', rc)
    
    def handle_post(self):
        self.form = BulkImportForm(self.request.POST, self.request.FILES)
        if not self.form.is_valid():
            d = {
                'form': self.form.as_p(),
                'json': self.get_org_json(),
                'errors':['Form is not valid, please review.'],
                'active': 'events'
            }
            rc = RequestContext(self.request, d)
            r = render_to_response('bulk_import.html', rc)
            r.status = 400

        self.project = get_object_or_404(Project, projname=self.form.cleaned_data['project'])
        organization = get_object_or_404(Organization, orgname=self.form.cleaned_data['organization'])

        try:
            datasheet_id = int(self.form.cleaned_data['datasheet'])
        except ValueError:
            raise Http404()
        self.data_sheet = get_object_or_404(DataSheet, id=datasheet_id)

        # validate the datasheet
        if not self._validate_data_sheet():
            return 
        
        # validate CSV schema (headers)
        if not self._read_csv():
            return
        
        
        # create a transaction for data import and validate the data
        self.user_txn = UserTransaction(submitted_by=self.request.user, status='new', 
                                        organization=organization, 
                                        project=self.project)
        self.user_txn.save()
        if not self.user_txn.id: 
            self.response = render_to_response('bulk_import.html', RequestContext(self.request,{'form':self.form.as_p(), 
                'errors':['Could not complete the transaction at this time.',], 'active':'events', 'json':self.get_org_json()}))
            self.response.status_code = 400
            return

        self._validate_csv_rows()
        
        if not self._check_site_keys():
            return
        
        if not self._write_csv_rows():
            return
    
    @Timer.timed_function
    def _validate_data_sheet(self):
        """Make sure the data sheet is set up for bulk imports 
        (that it has required the fields).
        """
        valid, message = self.data_sheet.is_valid()
        if not valid: 
            errors = ["""Sorry. This datasheet is not configured handle bulk imports.
                    Please notify the database administrator and it will be fixed ASAP.""", ]
            self.logger.error(message)
            self.response = bulk_bad_request(self.form, self.request, errors, 
                                             json=self.get_org_json())
            return False
        return True

    @Timer.timed_function
    def _read_csv(self):
        """Read and validate the CSV file.
        """
        reader = csv.DictReader(self.request.FILES['csv_file'])

        # check for missing or extra fields
        self.csv_fields = set(reader.fieldnames)
        required_fields = set(self.data_sheet.required_fieldnames())
        all_fields = set(self.data_sheet.fieldnames())
        missing_fields = required_fields - self.csv_fields
        extra_fields = self.csv_fields - all_fields
        
        # maybe produce one error for "Missing column" + join missing column 
        # names instead of producing an error for every missing column...? 
        self.errors = [
            "Uploaded file does not contain required column '%s'" % (e)
            for e in missing_fields] 

        self.errors.extend(["Uploaded file contains column '%s' which is not recognized by this datasheet" % (e)
                       for e in extra_fields])
        if self.errors:
            self.response = bulk_bad_request(self.form, self.request, self.errors, 
                                             json=self.get_org_json())
            return False
        
#         self.data = [BulkImportRow(row) for row in reader][:10]
        def c():
            self.data = list(reader)
        c = Timer.timed_function(c)
        c()
#         self.data = list(reader) # read all CSV rows ~ 275ms for 4500 rows!
        return True
    
    @Timer.timed_function
    def _validate_csv_rows(self):
        """Validate rows against form and collect Sites.
        """
        # construct a QueryDict to supply CSV data to the DataSheetForm for 
        # validation
        self.unique_site_keys = []
        qd = QueryDict('').copy() 
        field_name_id_map = dict(res for res in self.data_sheet.datasheetfield_set.values_list('field_name', 'pk'))
        for i, row in enumerate(self.data):
            # populate the query dict with data from the current row
            for k, v in row.iteritems():
                qd['question_%d' % field_name_id_map[k]] = v

            # Use the DataSheetForm to validate the row
            data_sheet_form = DataSheetForm(self.data_sheet, None, None, qd)
            if not data_sheet_form.is_valid():
                # extract the errors from the form and put them into the error
                # collection
                for question, message in data_sheet_form.errors.items():
                    fieldnum = int(question.replace('question_', ''))
                    fieldname = self.data_sheet.datasheetfield_set.filter(pk=fieldnum).values_list('field_name', flat=True)
                    self.errors.append("Row %d, column <em>'%s'</em><br/>%s" % (i+2, fieldname, message.as_text().replace("* ","")))

            # TODO: move date validation into the DataSheetForm
            # Validate the required 'date' field
            try: 
                parse_date(date_string = get_required_val(self.data_sheet,'date', row))
            except ValueError:
                # i + 2 => convert to 1s indexing and skip the header row, so the row numbers match what would show up in Excel
                self.errors.append("Row %d, Invalid Date." % (i+2,))

            try:
                site_key = get_site_key(self.data_sheet, row)
                if site_key not in self.unique_site_keys:
                    self.unique_site_keys.append(site_key)
            except State.DoesNotExist:
                self.errors.append("Row %d, Invalid state name" % (i+2, ))
            except LatLonError:
                self.errors.append("Row %d, Invalid Latitude/Longitude. Use decimal degrees." % (i+2, ))

        # if self.errors:
        #     fail? Return a bad bulk request? 

    @Timer.timed_function
    def _check_site_keys(self):
        """Find any sites referenced in the CSV and create them if they don't
        exist.
        """
        self.sites = []
        for site_key in self.unique_site_keys:
            site_text = ', '.join([str(x) for x in site_key.values()])
            try:
                site = Site.objects.filter(**site_key)[0] # silent fail and grab first if not unique
                self.sites.append({'name':site_text, 'site':site})
            except IndexError:
                if self.data_sheet.site_type == 'coord-based':
                    # just insert it 
                    lon = float(site_text.split('(')[1].split(' ')[0])
                    lat = float(site_text.split(' ')[1].split(')')[0])
                    point = Point(lon, lat)
                    closest = impute_state_county(point)
                    if not closest['error']:
                        site, created = Site.objects.get_or_create(state=closest['state'], 
                                                                   county=closest['county'], 
                                                                   geometry=str(point),
                                                                   transaction=self.user_txn)
                        if site:
                            self.sites.append({'name':site_text, 'site':site})
                    else:
                        self.errors.append("""%s""" % closest['error'])

                else:
                    urlargs = urlencode(site_key) 
                    if urlargs:
                        urlargs = "?" + urlargs

                    self.errors.append("""Site <em>'%s'</em> is not in the database. <br/>
                    <button href="/site/create%s" class="btn btn-mini create-site" disabled> Create new site record </button>
                    <!--<a href="/site/list" class="btn btn-mini"> Match to existing site record </a>-->
                    """ % (site_text, urlargs ))
                    self.sites.append({'name':site_text, 'site':None})

        if len(self.errors) > 0:
            site_form = CreateSiteForm()
            self.user_txn.delete()
            self.response = bulk_bad_request(self.form, self.request, 
                                             self.errors, 
                                             site_form=site_form, 
                                             json=self.get_org_json())
            return False
        return True

    @Timer.timed_function
    @transaction.commit_on_success
    def _write_csv_rows(self):
        # loop through rows to create events and submit datasheet forms
        
        # A list of events processed is passed into the bulk import template
        events = []
        field_value_bulk_insert_generators = []
        dups = 0
        # a count of all rows we've seen
        event_count = 0

        for row in self.data:
            t = Timer()
            event_count += 1
            site_key = get_site_key(self.data_sheet, row)
#             print "Time to get site_key %.2f ms" % t.elapsed(t.MILLISECONDS)
            try:
                site = Site.objects.get(**site_key)
            except Site.DoesNotExist:
                print "Error, site", str(site_key), "does not exist"
                raise
#             print "Time to get site object %.2f ms" % t.elapsed(t.MILLISECONDS)
            date_string = get_required_val(self.data_sheet,'date', row)
            date = parse_date(date_string)
    
            event = Event(datasheet_id=self.data_sheet, proj_id=self.project,
                          cleanupdate=date, site=site, 
                          transaction=self.user_txn)
            events.append(event)
            try:
                sid = transaction.savepoint()
                # print "Trying to save event"
                event.save()
            except IntegrityError as e:
                # print "IntegrityError inserting event", str(e)
                # print "Event save failed", str(e), "Ignoring duplicates"
                #transaction.savepoint_rollback(sid)
                #continue
                if e.message.startswith('duplicate key value violates unique constraint "core_event'):
                    transaction.savepoint_rollback(sid)
    
                    # check against ALL events that match
                    existing_events = Event.objects.filter(datasheet_id=self.data_sheet, 
                                                           proj_id=self.project, 
                                                           cleanupdate=date,
                                                           site=site)
    
                    # compare existing values to the current row's values 
                    # i.e. determine if it is indeed a new event or a true duplicate
                    new_event = False
                    t = Timer()
                    for e in existing_events: # this loop is ~ 150ms per iteration * 50 iterations per duplicate row. I.e., lots. I'm not sure it should be happening at all, I still think we can safely ignore the duplication check. 
                        # print "Checking existing events in", str(e)
                        
                        # switching to the generator saves 500ms per loop
                        for k, v in e.field_values_gen():
                            # print "Checking existing items", k
                            existing_val_raw = v[0]
                            dtype = v[1]
    
                            try:
                                row_val_raw = row[k]
                            except KeyError:
                                row_val_raw = None
    
                            if existing_val_raw in [u'None', u'', None]:
                                if row_val_raw is not None and row_val_raw != '':
                                    new_event = True
                                    break
                                else: 
                                    continue
    
                            if dtype in ['Area', 'Distance', 'Duration', 'Number', 'Volume', 'Weight']: 
                                try:
                                    if float(existing_val_raw) != float(row_val_raw):
                                        new_event = True
                                        break
                                except ValueError:
                                    if existing_val_raw != row_val_raw:
                                        new_event = True
                                        break
                            elif dtype == 'Date':
                                try:
                                    extdate = parse_date(existing_val_raw)
                                    rowdate = parse_date(row_val_raw)
                                    if extdate != rowdate:
                                        new_event = True
                                        break
                                except ValueError:
                                    if existing_val_raw != row_val_raw:
                                        new_event = True
                                        break
                            else: #text
                                if existing_val_raw != row_val_raw:
                                    new_event = True
                                    break
                        
                        if new_event:
                            # Oops, don't forget to break out of the OUTER loop too
                            break
                        # print t.lap(t.MILLISECONDS), t.average(t.MILLISECONDS)
                    # print t.elapsed(t.MILLISECONDS)

                    if new_event: 
                        # increment the event dup id
                        maxdup = existing_events.aggregate(Max('dup')).get('dup__max')
    
                        # and try again to create the event
                        event.dup = maxdup + 1
                        try:
                            event.save()
                        except IntegrityError as e:
                            if e.message.startswith('duplicate key value violates unique constraint "core_event'):
                                dups += 1
                                self.errors.append('Duplicate event already exists <br> (%s, %s, %s, %s)' % (self.project.projname,
                                    self.data_sheet, site.sitename, date))
                                events.pop() # toss out the last event
                                continue
                    else:
                        dups += 1
                        self.errors.append('Duplicate Event <br/> (%s, %s, %s, %s)' % (self.project.projname,
                            self.data_sheet.sheetname, site.sitename, date))
                        events.pop()    # toss out the last event
                        continue
                else:
                    raise e # something unexepected
            
            qd = get_querydict(self.data_sheet, row)
            ds_final_form = DataSheetForm(self.data_sheet, event, None, qd)
            if ds_final_form.is_valid():
                field_value_bulk_insert_generators.append(ds_final_form.bulk_create_generator(self.data_sheet))
            else:
                raise Exception("""Somehow the datasheetform is now invalid 
                  (despite just validating it previously without event)... errors are '%s'""" % str(ds_final_form.errors))
    
        if len(self.errors) > 0:
            if len(events) > 0:
                # Some events were loaded, so show the number loaded as an error
                self.errors = ["%d of %d loaded (%d duplicates ignored)" % (len(events), event_count, dups)]
            elif len(events) == 0:
                # Only bail out if there were no events loaded
                self.errors = ["No events loaded. (%d events processed, %d were duplicates)" % (event_count, dups)]
                transaction.rollback()
                self.user_txn.delete()
                self.response = bulk_bad_request(self.form, self.request, self.errors)
                return False
        
        chain = itertools.chain(*field_value_bulk_insert_generators)
        
        try:
            FieldValue.objects.bulk_create(chain)
        except Exception as e:
            self.errors.append("An internal error occured while saving the form. Please contact the database administrator.")
            self.response = bulk_bad_request(self.form, self.request, 
                                             self.errors)
            self.logger.error(unicode(e))
            return False 
                
        self.response = render_to_response('bulk_import.html', RequestContext(self.request,{'dups': dups, 'form':self.form.as_p(),
            'sites': self.sites, 'events': events, 'success': True, 'active':'events', 'json':self.get_org_json()}))
        return True

    def get_org_json(self):
        """Get all the organizations, projects, datasheets, datasheet fields, 
        and convert them to JSON. 
        """
        org_dicts = [o.toDict for o in Organization.objects.all()]
        return simplejson.dumps(org_dicts)

def bulk_import_post(request, org_json):
    logger = logging.getLogger('datasheet_errors')
    #TODO: Filter Organizations by only those which the user has access to.

    form = BulkImportForm(request.POST, request.FILES)
    if form.is_valid():
        rows = csv.DictReader(request.FILES['csv_file'])
        
        # rows = list(rows) # eval now so we can do multiple loops
        rows = list(yield_some(rows, 40))

        if len(rows) == 0:
            return bulk_bad_request(form, request, ['Uploaded file does not contain any rows.', ], json=org_json)
        
        # Get the datasheet. Must post a datasheet_id variable
        try:
            datasheet_id = request.POST['datasheet']
        except KeyError:
            return bulk_bad_request(form, request, ['Form is not valid, please review.', ], json=org_json)

        ds = get_object_or_404(DataSheet, id=int(datasheet_id))

        valid, message = ds.is_valid()
        if not valid:
            errors = ["""Sorry. This datasheet is not configured handle bulk imports.
                    Please notify the database administrator and it will be fixed ASAP.""", ]
            logger.error(message)
            return bulk_bad_request(form, request, errors, json=org_json)

        errors = []

        # TODO: move this into a validate_columns() function, figure out some strategy to deal with the errors[] array
         
        # confirm required columns
        all_fieldnames = ds.fieldnames
        csv_file_columns = rows[0].keys()
        for rf in ds.required_fieldnames():
            if rf not in csv_file_columns: # or row[rf] is None:   # when would the row value be None? Wouldn't csv.DictReader replace it with an empty string if there were no data (,, in the csv)?
                errors.append("Uploaded file does not contain required column '%s'" % (rf,))
        for key in csv_file_columns:
            if key not in all_fieldnames:
                errors.append("Uploaded file contains column '%s' which is not recognized by this datasheet" % (key,))
        if len(errors) > 0:
            # return at the datasheet level
            return bulk_bad_request(form, request, errors, json=org_json)

        # loop through rows and validate against forms
        # also collect sites
        unique_site_keys = []
        for i, row in enumerate(rows):
            qd = get_querydict(ds, row)
            ds_form = DataSheetForm(ds, None, None, qd)
            if not ds_form.is_valid():
                for question, message in ds_form.errors.items():
                    fieldnum = int(question.replace("question_",''))
                    fieldname = ds.datasheetfield_set.get(pk=fieldnum).field_name
                    errors.append("Row %d, column <em>'%s'</em><br/>%s" % (i+2, fieldname, message.as_text().replace("* ","")))
            
            # TODO: move date validation into the DataSheetForm
            try: 
                parse_date(date_string = get_required_val(ds,'date', row))
            except ValueError:
                # i + 2 => convert to 1s indexing and skip the header row, so the row numbers match what would show up in Excel
                errors.append("Row %d, Invalid Date." % (i+2,))

            try:
                site_key = get_site_key(ds, row)
                if site_key not in unique_site_keys:
                    unique_site_keys.append(site_key)
            except State.DoesNotExist:
                errors.append("Row %d, Invalid state name" % (i+2, ))
            except LatLonError:
                errors.append("Row %d, Invalid Latitude/Longitude. Use decimal degrees." % (i+2, ))
        
        sites = []

        project = Project.objects.get(projname=form.data['project'])
        organization = Organization.objects.get(orgname=form.data['organization'])
        user_transaction = UserTransaction(submitted_by=request.user, 
                                           status='new', 
                                           organization=organization, 
                                           project=project)
        user_transaction.save()
        if user_transaction.id:
            site_count = 0
            # print("Unique site keys:", unique_site_keys)
            for site_key in unique_site_keys:
                site_text = ', '.join([str(x) for x in site_key.values()])
                try:
                    site = Site.objects.filter(**site_key)[0] # silent fail and grab first if not unique
                    sites.append({'name':site_text, 'site':site})
                except IndexError:
                    if ds.site_type == 'coord-based':
                        # just insert it 
                        lon = float(site_text.split('(')[1].split(' ')[0])
                        lat = float(site_text.split(' ')[1].split(')')[0])
                        point = Point(lon, lat)
                        closest = impute_state_county(point)
                        if not closest['error']:
                            site, created = Site.objects.get_or_create(state=closest['state'], 
                                                                       county=closest['county'], 
                                                                       geometry=str(point))
                        else:
                            errors.append("""%s""" % closest['error'])
                            site = False
                            created = False
                        
                        if created:
                            site.transaction = user_transaction
                            site.save()
                        if site:
                            sites.append({'name':site_text, 'site':site})
                    else:
                        urlargs = urlencode(site_key) 
                        if urlargs:
                            urlargs = "?" + urlargs

                        errors.append("""Site <em>'%s'</em> is not in the database. <br/>
                        <button href="/site/create%s" class="btn btn-mini create-site" disabled> Create new site record </button>
                        <!--<a href="/site/list" class="btn btn-mini"> Match to existing site record </a>-->
                        """ % (site_text, urlargs ))
                        sites.append({'name':site_text, 'site':None})

            if len(errors) > 0:
                site_form = CreateSiteForm()
                UserTransaction.delete(user_transaction)
                return bulk_bad_request(form, request, errors, site_form=site_form, json=org_json)

            # valid!
            # loop through rows to create events and submit datasheet forms
            events = []
            dups = 0
            with transaction.commit_on_success():
                for i, row in enumerate(rows):
                    site_key = get_site_key(ds, row)
                    site = Site.objects.filter(**site_key)[0]
                    date_string = get_required_val(ds,'date', row)
                    date = parse_date(date_string)

                    project = get_object_or_404(Project, projname=form.cleaned_data['project'])
                    event = Event(
                        datasheet_id = ds,
                        proj_id = project, # get this at the row level? or the bulk import level?
                        cleanupdate = date,
                        site = site,
                        transaction = user_transaction
                    )
                    events.append(event)
                    try:
                        sid = transaction.savepoint()
                        # print "Trying to save event"
                        event.save()
                    except IntegrityError as e:
                        # print "Event save failed", str(e), "Ignoring duplicates"
                        # transaction.savepoint_rollback(sid)
                        # continue
                        if e.message.startswith('duplicate key value violates unique constraint "core_event'):
                            transaction.savepoint_rollback(sid)

                            # check against ALL events that match
                            existing_events = Event.objects.filter(datasheet_id = ds, proj_id = project, cleanupdate = date, site = site)

                            # compare existing values to the current row's values 
                            # i.e. determine if it is indeed a new event or a true duplicate
                            new_event = False
                            for e in existing_events:
                                # print "Checking existing events in", str(e)
                                existing = e.field_values

                                for k, v in existing.items():
                                    # print "Checking existing items", k
                                    existing_val_raw = v[0]
                                    dtype = v[1]

                                    try:
                                        row_val_raw = row[k]
                                    except KeyError:
                                        row_val_raw = None

                                    if existing_val_raw in [u'None', u'', None]:
                                        if row_val_raw is not None and row_val_raw != '':
                                            new_event = True
                                            break
                                        else: 
                                            continue

                                    if dtype in ['Area', 'Distance', 'Duration', 'Number', 'Volume', 'Weight']: 
                                        try:
                                            if float(existing_val_raw) != float(row_val_raw):
                                                new_event = True
                                                break
                                        except ValueError:
                                            if existing_val_raw != row_val_raw:
                                                new_event = True
                                                break
                                    elif dtype == 'Date':
                                        try:
                                            extdate = parse_date(existing_val_raw)
                                            rowdate = parse_date(row_val_raw)
                                            if extdate != rowdate:
                                                new_event = True
                                                break
                                        except ValueError:
                                            if existing_val_raw != row_val_raw:
                                                new_event = True
                                                break
                                    else: #text
                                        if existing_val_raw != row_val_raw:
                                            new_event = True
                                            break
                                
                                if new_event:
                                    break

                            if new_event: 
                                # increment the event dup id
                                try:
                                    maxdup = max([x.dup for x in existing_events])
                                except ValueError:
                                    maxdup = 0

                                # and try again to create the event
                                event = Event(
                                    datasheet_id = ds,
                                    proj_id = project,
                                    cleanupdate = date,
                                    site = site,
                                    dup = maxdup + 1,
                                    transaction = user_transaction
                                )
                                try:
                                    event.save()
                                except IntegrityError as e:
                                    if e.message.startswith('duplicate key value violates unique constraint "core_event'):
                                        dups += 1
                                        errors.append('Duplicate event already exists <br> (%s, %s, %s, %s)' % (project.projname,
                                            ds.sheetname, site.sitename, date))
                                        continue
                            else:
                                dups += 1
                                errors.append('Duplicate Event <br/> (%s, %s, %s, %s)' % (project.projname,
                                    ds.sheetname, site.sitename, date))
                                continue
                        else:
                            raise e # something unexepected

                    qd = get_querydict(ds, row)
                    ds_final_form = DataSheetForm(ds, event, None, qd)
                    if ds_final_form.is_valid():
                        try:
                            ds_final_form.save(ds)
                        except Exception as e:
                            logger.error(unicode(e)) 
                            errors.append("An internal error occured while saving the form. Please contact the database administrator.")
                    else:
                        raise Exception("""Somehow the datasheetform is now invalid 
                          (despite just validating it previously without event)... errors are '%s'""" % str(ds_final_form.errors))

                if len(errors) > 0:
                    transaction.rollback()
                    if len(events) > 0 and dups > 0:
                        errors.insert(0, "%d events were found but not loaded due to %d duplicate events." % (len(events), dups))
                    UserTransaction.delete(user_transaction)
                    return bulk_bad_request(form, request, errors)

            return render_to_response('bulk_import.html', RequestContext(request,{'form':form.as_p(),
                'sites': sites, 'events': events, 'success': True, 'active':'events', 'json':org_json}))
        else:
            UserTransaction.delete(user_transaction)
            res = render_to_response('bulk_import.html', RequestContext(request,{'form':form.as_p(), 
                'errors':['Could not complete the transaction at this time.',], 'active':'events', 'json':org_json}))
            res.status_code = 400
            return res
                    
    else:
        res = render_to_response('bulk_import.html', RequestContext(request,{'form':form.as_p(), 
            'errors':['Form is not valid, please review.',], 'json':org_json, 'active':'events'}))
        res.status_code = 400
        return res

    return render_to_response('bulk_import.html', RequestContext(request,{'form':form.as_p(), 'json':org_json, 'active':'events'}))


@login_required
def create_site(request):
    if request.method == 'GET':
        form = CreateSiteForm()
        sitename = request.GET.get('sitename')
        state = request.GET.get('state')
        county = request.GET.get('county')
        if sitename:
            ff = form.fields['sitename']
            ff.initial = sitename
            ff.widget.attrs['readonly'] = True
        if county:
            ff = form.fields['county']
            ff.initial = county 
            ff.widget.attrs['readonly'] = True
        if state:
            ff = form.fields['state']
            state_id = None
            for sid, sname in ff.choices:
                if sname == state:
                    state_id = sid
                    break
            if state_id:
                ff.initial = state_id
                ff.widget.attrs['readonly'] = True
        return render_to_response('create_site.html', RequestContext(request,{'form':form.as_p(), 'active':'events'}))
    else :
        form = CreateSiteForm(request.POST)
        if form.is_valid():
            form.save()
            blank_form = CreateSiteForm()
            return render_to_response('create_site.html', RequestContext(request,{'form':blank_form.as_p(), 'success': True, 'active':'events'}))
        else:
            res = render_to_response('create_site.html', RequestContext(request,{'form':form.as_p(), 
                'error':'Form is not valid, please review.', 'active':'events'}))
            res.status_code = 400
            return res

def get_downloads(request):
    ds = Download.objects.all().order_by('category')
    return render_to_response('downloads.html', RequestContext(request,{'downloads': ds}))


    
def impute_state_county(point):
        '''
        Based on the geometry, sets state and county
        '''
        pnt = point
        counties = County.objects.filter(geom__bboverlaps=pnt.buffer(1)) # search in a 1 degree radius
        deg_buffer = 1
        error = ''
        while counties.count() == 0 and deg_buffer < 50:
            deg_buffer += 1
            counties = County.objects.filter(geom__bboverlaps=pnt.buffer(deg_buffer)) # search in a {deg_buffer} degree radius
            
        if deg_buffer == 50:
            error = "Entered site is too far from land.<br />Double check coordinates:<br />%s, %s" % (point.coords[0], point.coords[1])

        closest = None
        shortest_distance = 181
        for county in counties:
            if county.geom.intersects(pnt):
                # direct hit
                closest = county
                break
            d = county.geom.distance(pnt)
            if d < shortest_distance:
                # look for the closest if no direct hit
                closest = county
                shortest_distance = d

        if not closest:
            res = {
                'county': None,
                'state': None,
                'error': error
            }
        else:
            res = {
                'county': closest.name,
                'state': State.objects.filter(initials=closest.stateabr)[0],
                'error': None
            }

        return res
    
