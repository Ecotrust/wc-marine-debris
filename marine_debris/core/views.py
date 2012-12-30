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
from django.contrib.gis.geos import Polygon, Point
from forms import *
from models import *
from sets import Set

import datetime
import time
import string
import logging
import csv

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
    return render_to_response( 'management.html', RequestContext(request))

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
            if status is not None:
                transaction.status = status
                if status == 'rejected' and reason is not None:
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
                        msg_details = msg_details + "\nEvent Project: %s\nSite: %s\nDate: %s\n" % (event.proj_id.projname, event.site.sitename, event.cleanupdate.isoformat())
                    
                    message = msg_header + msg_rejected + msg_footer + msg_details

                    user.email_user("Marine Debris DB Status Update", message)
                    
                transaction.update()
    else:
        res = {
            'status_code': 400,
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

sort_cols = {
    "site.st_initials": 'site__state',
    "datasheet.event_type": "datasheet_id__type_id",
    "site.name": "site__sitename",
    "site.county": "site__county",
    "date": "cleanupdate"
}

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
        d = event.toEventsDict
        evd = event.toValuesDict()
        d['field_values'] = evd
        all_fieldnames = Set(evd.keys()) | all_fieldnames
        data.append(d)

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
            if x[2]: # if units are defined
                header.append("%s (%s)" % (x[1], x[2]))
            else:
                header.append("%s" % x[1])
    else:
        header.extend([x[0] for x in ordered_fieldnames])

    row = ','.join(header)
    row += "\n"
    yield row

    for d in data:
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

        row = ','.join(['"%s"' % x for x in row_data])
        row += "\n"
        yield row

def download_events(request):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = request.GET.get('filename', 'WCGA_debris_%s' % timestamp )
    res = HttpResponse(download_stream_generator(request), content_type="text/csv")
    res['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename
    return res

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
        qs = Event.objects.all()

    if accepted_only:
        qs = qs.filter(transaction__status = "accepted")
    
    if sort_column:
        sort_name_key = request.GET.get("mDataProp_%s" % sort_column, False)
        sort_dir = request.GET.get("sSortDir_0", False)
        if sort_name_key:
            sort_name = sort_cols[sort_name_key]
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
    
def get_sites(request):
    sEcho = request.GET.get('sEcho', False)
    start_id = request.GET.get('startID', False)
    transaction = request.GET.get('transaction', False)

    if transaction:
        qs = Site.objects.filter(transaction__id=transaction)
    else:
        qs = Site.objects.all()

    filtered_count = qs.count()

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
    
def get_event_geojson(request):
    srid = settings.GEOJSON_SRID
    crs = srid_to_proj(srid)
    filter_json = request.GET.get('filter', False)
    bbox = request.GET.get('bbox', False)
    feature_jsons = []
    
    if filter_json and bbox:
        qs = Event.filter(simplejson.loads(filter_json), simplejson.loads(bbox))
    elif filter_json:
        qs = Event.filter(simplejson.loads(filter_json))
    else:
        qs = Event.objects.all()
    
    if not settings.DEMO:
        qs = qs.filter(transaction__status = "accepted")
    
    loop_count = 0
    
    for event in qs:
        loop_count = loop_count + 1
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

    for event in cleanup_events:
        datasheet = event.toEventsDict['datasheet']['name']
        if datasheet not in datasheets:
            datasheets.append(datasheet)
            
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
                field['num_values'] = field['num_values'] + 1
                #Collect data for high-level categories
                if db_field['display_category']['name'] not in ['Location', 'Date', 'Event', 'Debris', 'Mixed', ''] and (db_field['unit']['short_name'] == 'Count' or db_field['datatype']['name'] == 'Weight'):
                    if not categories.has_key(db_field['display_category']['name']):
                        categories[db_field['display_category']['name']] = {
                            'pounds': 0,
                            'count': 0
                        }
                    if db_field['datatype']['name'] == 'Weight':
                        if not db_field['unit']['short_name'] == 'lbs':
                            factor = Unit.get_conversion_factor(db_field['unit']['short_name'],'lbs')
                            lbs_val = factor * field_value['value']
                        else:
                            lbs_val = field_value['value']
                        categories[db_field['display_category']['name']]['pounds'] = categories[db_field['display_category']['name']]['pounds'] + float(lbs_val)
                    else:
                        categories[db_field['display_category']['name']]['count'] = categories[db_field['display_category']['name']]['count'] + float(field_value['value'])
                        
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
                datasheetForm.save()
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
    field_names = ds.fieldnames
    header = ','.join(["\"%s\"" % f for f in field_names])
    test_row = '' #TODO put valid default values?
    filename = slugify(ds.sheetname) + ".csv"
    response = HttpResponse('\n'.join([header, test_row]) , mimetype="text/csv")
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

def bulk_bad_request(form, request, errors=None, site_form=None):
    if not errors:
        errors = []
    res = render_to_response('bulk_import.html', 
            RequestContext(request,{'form':form.as_p(), 'site_form': site_form, 
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

            project = Project.objects.get(id=form.data['project_id'])
            organization = Organization.objects.get(orgname=form.data['organization'])
            user_transaction = UserTransaction(submitted_by = request.user, status = 'new', organization=organization, project=project)
            user_transaction.save()
            if user_transaction.id:
                for site_key in unique_site_keys:
                    site_text = ', '.join([str(x) for x in site_key.values()])
                    try:
                        site = Site.objects.filter(**site_key)[0] # silent fail and grab first if not unique
                        sites.append({'name':site_text, 'site':site})
                    except IndexError:
                        if ds.site_type == 'coord-based':
                            # just insert it 
                            site, created = Site.objects.get_or_create(**site_key)
                            if created:
                                site.transaction = user_transaction
                            site.save()
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
                    return bulk_bad_request(form, request, errors, site_form=site_form)

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
                            transaction = user_transaction
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
                UserTransaction.delete(user_transaction)
                res = render_to_response('bulk_import.html', RequestContext(request,{'form':form.as_p(), 
                    'errors':['Could not complete the transaction at this time.',], 'active':'events'}))
                res.status_code = 400
                return res
                        
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

def get_downloads(request):
    ds = Download.objects.all().order_by('category')
    return render_to_response('downloads.html', RequestContext(request,{'downloads': ds}))


    
