from django import template
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, QueryDict
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.views import login as default_login, logout as default_logout
from django.utils import simplejson
from django.forms.models import modelformset_factory
from django.contrib.gis.geos import Point
from django.utils.http import urlencode
from django.core.cache import cache
from django.contrib.gis.geos import Polygon

import datetime
import string
import logging
import csv
from forms import *
from models import *


def index(request): 

    event_count = [
        {
            "type": "Site Cleanup",
            "count": Event.objects.filter(datasheet_id__type_id__type = "Site Cleanup").count(),
        },
        {
            "type" : "Gear Removal",
            "count": Event.objects.filter(datasheet_id__type_id__type = "Gear Removal").count()
        }
    ]
    
    if settings.SERVER == 'Dev':
        static_media_url = settings.MEDIA_URL
    else:
        static_media_url = settings.STATIC_URL

    return render_to_response( 'index.html', RequestContext(request,{'STATIC_URL':static_media_url, 'thankyou': False, 'active':'home', 'event_count': event_count}))

def events(request, submit=False): 

    if submit:
        return render_to_response( 'events.html', RequestContext(request,{'submit':True, 'added_site':submit, 'active':'events'}))
    else:
        return render_to_response( 'events.html', RequestContext(request,{'submit':submit, 'added_site':None, 'active':'events'}))
        
def get_locations(request):
    states = []
    locations = {}
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
    return HttpResponse(simplejson.dumps({
        'states': states,
        'locations': locations,
    }))

sort_cols = {
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

    if filter_json:
        filters = simplejson.loads(filter_json)
        qs = Event.filter(filters)
    else:
        qs = Event.objects.all()

    if sort_column:
        sort_name_key = request.GET.get("mDataProp_%s" % sort_column, False)
        sort_dir = request.GET.get("sSortDir_0", False)
        if sort_name_key:
            sort_name = sort_cols[sort_name_key]
            if sort_dir == 'desc':
                sort_name = "-" + sort_name
            qs = qs.order_by(sort_name)
    filtered_count = qs.count()
    if count and not start_id:
        qs = qs[int(start_index):int(start_index) + int(count)]

    data = []
    found_records = 0

    timeout=60*60*24*7*52*10
    for event in qs: 
        key = 'eventcache_%s' % event.id
        dict = cache.get(key)
        if not dict:
            dict = event.toEventsDict
            cache.set(key, dict, timeout)
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
            
            
    res = {
       "aaData": data,
       "iTotalRecords": Event.objects.all().count(),
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
    
def get_event_geojson(request):
    srid = settings.GEOJSON_SRID
    crs = srid_to_proj(srid)
    filter_json = request.GET.get('filter', False)
    feature_jsons = []
    
    if filter_json:
        qs = Event.filter(simplejson.loads(filter_json))
    else:
        qs = Event.objects.all()
    
    timeout=60*60*24*7*52*10
    loop_count = 0
    for event in qs:
        print loop_count
        loop_count = loop_count + 1
        key = 'geocache_%s' % event.id
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
            cache.set(key, geo_string, timeout)
        feature_jsons.append(geo_string)
        
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
        
def get_event_values_list(request, filters=None):
    
    # type = 'Site Cleanup'   #TODO: get this type name dynamically so we can show derelict and others
    # field_list = None
    # key = False
    # if not filters:    
        # timeout = 60*60*24*7
        # key = "reportcache_%s" % type.replace(" ","_")
        # field_list = cache.get(key)
    # if not field_list:
        # cleanup_events = Event.objects.filter(datasheet_id__type_id__type = type)
        # if filters:
    cleanup_events = Event.filter(filters)
    agg_fields = {}

    field_values = FieldValue.objects.filter(event_id__in = cleanup_events, field_id__datatype__aggregatable = True)
    
    for field_value in field_values:
        field_name = field_value.field_id.internal_name
        if field_value.field_value and not field_value.field_value in ['', None, 'None']:
            if not agg_fields.has_key(field_name):
                agg_fields[field_name] = get_agg_template(field_value.field_id)
            field = agg_fields[field_name]
            
            
            if not field['value']:
                field['value'] = 0
            
            field['value'] = field['value'] + float(field_value.field_value)
            if field['unit'].__len__() == 0:
                ds = field_value.event_id.datasheet_id
                unit = DataSheetField.objects.get(sheet_id = ds, field_id = field_value.field_id).unit_id.short_name
                if unit in ['dd', 'dd mm.mm', 'ft', 'kg', 'km', 'mi', 'mm', 'mm.000', '%', 'lbs', 'sq ft']:
                    field['unit'] = [unit]
                else:
                    field['unit'] = [' ']
            # else:     #TODO: get translators in here to handle converting unit types and feeding a whole selection of values
     
    field_list = []
    for agg_field in agg_fields:
        field_list.append({
            'field': agg_fields[agg_field]
        })
    # if key:
        # cache.set(key, field_list, timeout)
            
    return field_list
    
def get_agg_template(field):
    return {
        'name': field.internal_name,
        'type': field.datatype.name,
        'unit': [],
        'value': None
    }
    
def get_event_values(request):
    filters = request.GET.get('filters', None)
    if filters:
        filters = simplejson.loads(filters)
    field_list = get_event_values_list(request, filters)
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
            datasheetName = DataSheet.objects.get(id=form.data['data_sheet']).sheetname
            event['data_sheet'] = datasheetName
            
            datasheet = DataSheet.objects.get(sheetname=event['data_sheet'])
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
def event_location(request):
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
        form = DataSheetForm(datasheet, None, request.POST)
        

        return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p(), 'eventForm': eventForm.as_p(), 'event':event, 'active':'events'}))
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
        project = Project.objects.get(projname=createEventForm.data['project'])
        datasheet = DataSheet.objects.get(id=createEventForm.data['data_sheet'])
        state = State.objects.get(initials=createEventForm.data['state'])
        point = Point(float(createEventForm.data['longitude']), float(createEventForm.data['latitude']))
        
        if datasheet.type_id.display_sites:        
            sitename = createEventForm.data['sitename']
        else:
            sitename = "%s, %s" % (createEventForm.data['longitude'], createEventForm.data['latitude'])

        if createEventForm.data['county'] == '':
            site = Site.objects.get_or_create(state = state, geometry = str(point), sitename = sitename)
        else:
            county = createEventForm.data['county']
            if Site.objects.filter(state=state, county=county, geometry = str(point), sitename = sitename).count() == 0:
                if Site.objects.filter(state=state, county=county+' County', geometry = str(point), sitename = sitename).count() > 0:
                    county = county + ' County'
            site = Site.objects.get_or_create(state = state, county = county, geometry = str(point), sitename = sitename)
        
        date = datetime.datetime.strptime(createEventForm.data['date'], '%m/%d/%Y')
        event = Event(proj_id = project, datasheet_id = datasheet, cleanupdate = date, site = site[0], submitted_by = request.user)
        event.save()
        if event.id:
            datasheetForm = DataSheetForm(event.datasheet_id, event, None, request.POST)
        if event.id and datasheetForm.is_valid():
            datasheetForm.save()
            return HttpResponseRedirect('/events/%s' % event.id)
        else:
            Event.delete(event)
            if site[1]:
                Site.delete(site[0])
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
    fields = simplejson.dumps({
        "fields": event.field_values_list,
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
    qs = DataSheet.objects.filter()
    result = []
    for datasheet in qs.all():
        result.append({'datasheet': datasheet})
        
    return render_to_response('datasheets.html', RequestContext(request, {'result':result, 'active':'datasheets'}))
    
@login_required
def edit_datasheet(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'GET':
        form = DataSheetForm(event.datasheet_id, event, None)
        event_details = {
            'organization': event.proj_id.projectorganization_set.get(is_lead=True).organization_id.orgname,
            'project': event.proj_id.projname,
            'date': event.cleanupdate,
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
            'date': event.cleanupdate,
            'data_sheet': event.datasheet_id.sheetname,
            'state': event.site.state.name,
            'latitude': event.site.lat,
            'longitude': event.site.lon
        }
        if event.datasheet_id.type_id.display_sites:
            event_details['county'] = event.site.county
            event_details['sitename'] = event.site.sitename
        return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p(), 'eventForm': None, 'event': event_details, 'action': '/datasheet/edit/'+str(event.event_id), 'active': 'events', 'error':'Some answers were invalid. Please review them.'}))
    
    
# @login_required
def organizations(request): 
    qs = Organization.objects.filter()
    result = []
    for organization in qs.all(): 
        result.append({'organization':organization})
            
    return render_to_response( 'organizations.html', RequestContext(request,{'result':result, 'active':'organizations'}))

# @login_required
def projects(request): 
    qs = Project.objects.filter()
    result = []
    for project in qs.all(): 
        result.append({'project':project})
            
    return render_to_response( 'projects.html', RequestContext(request,{'result':result, 'active':'projects'}))    

def map_test(request):
    return render_to_response('map-test.html', RequestContext(request, {}))

def bulk_csv_header(request, datasheet_id):
    ds = DataSheet.objects.get(id=datasheet_id)
    field_names = ds.fieldnames
    header = ','.join(["\"%s\"" % f for f in field_names])
    test_row = '' #TODO put valid default values?
    filename = slugify(ds.sheetname) + ".csv"
    response = HttpResponse('\n'.join([header, test_row]) , mimetype="text/csv")
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

def bulk_bad_request(form, request, errors=None):
    if not errors:
        errors = []
    res = render_to_response('bulk_import.html', 
            RequestContext(request,{'form':form.as_p(), 
                'errors':errors, 'active':'events'}))
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
    internal_name = settings.REQUIRED_FIELDS[ds.site_type][key]
    dsf = ds.datasheetfield_set.get(field_id__internal_name=internal_name)
    return row[dsf.field_name] # the header as it appears in the datasheet 

def get_state(statename):
    statename = statename.strip()
    try:
        state = State.objects.get(name__iexact=statename)
    except State.DoesNotExist:
        state = State.objects.get(initials__iexact=statename)
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
    field_id_lookup = dict([(f.field_name, f.id) for f in ds.datasheetfield_set.all()])

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
def bulk_import(request):
    if request.method == 'GET':
        form = BulkImportForm() # instance=ds)
    else:
        logger = logging.getLogger('datasheet_errors')
        form = BulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            rows = csv.DictReader(request.FILES['csvfile'])
            rows = list(rows) # eval now so we can do multiple loops
            if len(rows) == 0:
                return bulk_bad_request(form, request, ['Uploaded file does not contain any rows.', ])
            
            # Get the datasheet. Must post a datasheet_id variable
            try:
                datasheet_id = request.POST['datasheet_id']
            except KeyError:
                return bulk_bad_request(form, request, ['Form is not valid, please review.', ])

            ds = get_object_or_404(DataSheet, pk=datasheet_id)
            valid, message = ds.is_valid() 
            if not valid:
                errors = ["""Sorry. This datasheet is not configured handle bulk imports. 
                        The database administrator has been notified and will fix the problem ASAP.""", ]
                logger.error(message) 
                return bulk_bad_request(form, request, errors)

            errors = []

            # confirm required columns
            required_fieldnames = ds.required_fieldnames
            all_fieldnames = ds.fieldnames
            for i, row in enumerate(rows):
                keys = row.keys()
                for rf in required_fieldnames:
                    if rf not in keys or row[rf] is None:
                        errors.append("Uploaded file does not contain required column '%s'" % (rf,))
                for key in keys:
                    if key not in all_fieldnames:
                        errors.append("Uploaded file contains column '%s' which is not recognized by this datasheet" % (key,))
                if len(errors) > 0:
                    # return at the datasheet level
                    return bulk_bad_request(form, request, errors)

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
                
                try: 
                    parse_date(date_string = get_required_val(ds,'date', row))
                except ValueError:
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
            for site_key in unique_site_keys:
                site_text = ', '.join([str(x) for x in site_key.values()])
                try:
                    site = Site.objects.filter(**site_key)[0] # silent fail and grab first if not unique
                    sites.append({'name':site_text, 'site':site})
                except IndexError:
                    if ds.site_type == 'coord-based':
                        # just insert it 
                        site, created = Site.objects.get_or_create(**site_key)
                        site.save()
                        sites.append({'name':site_text, 'site':site})
                    else:
                        urlargs = urlencode(site_key) 
                        if urlargs:
                            urlargs = "?" + urlargs

                        errors.append("""Site <em>'%s'</em> is not in the database. <br/>
                        <a href="/site/create%s" class="btn btn-mini"> Create new site record </a>
                        <a href="/site/list" class="btn btn-mini"> Match to existing site record </a>
                        """ % (site_text, urlargs ))
                        sites.append({'name':site_text, 'site':None})

            if len(errors) > 0:
                return bulk_bad_request(form, request, errors)

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

                    project = get_object_or_404(Project, id=int(form.cleaned_data['project_id']))
                    event = Event(
                        datasheet_id = ds,
                        proj_id = project, # get this at the row level? or the bulk import level?
                        cleanupdate = date,
                        site = site,
                        submitted_by = request.user,
                        status = 'New' 
                    )
                    events.append(event)
                    try:
                        sid = transaction.savepoint()
                        event.save()
                    except IntegrityError as e:
                        if e.message.startswith('duplicate key value violates unique constraint "core_event'):
                            transaction.savepoint_rollback(sid)

                            # check against ALL events that match
                            existing_events = Event.objects.filter(datasheet_id = ds, proj_id = project, cleanupdate = date, site = site)

                            # compare existing values to the current row's values 
                            # i.e. determine if it is indeed a new event or a true duplicate
                            new_event = False
                            for e in existing_events:
                                existing = e.field_values

                                for k, v in existing.items():
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
                                    submitted_by = request.user,
                                    dup = maxdup + 1,
                                    status = 'New' 
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
                            ds_final_form.save()
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
                    return bulk_bad_request(form, request, errors)

            return render_to_response('bulk_import.html', RequestContext(request,{'form':form.as_p(), 
                'sites': sites, 'events': events, 'success': True, 'active':'events'}))
        else:
            res = render_to_response('bulk_import.html', RequestContext(request,{'form':form.as_p(), 
                'errors':['Form is not valid, please review.',], 'active':'events'}))
            res.status_code = 400
            return res

    #TODO: Filter Organizations by only those which the user has access to.
    org_dict = [org.toDict for org in Organization.objects.all()]
    org_json = simplejson.dumps(org_dict)
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
