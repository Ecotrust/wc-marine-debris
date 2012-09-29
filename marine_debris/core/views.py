from django import template
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, QueryDict
from models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.views import login as default_login, logout as default_logout
import datetime
import string
from django.utils import simplejson
import datetime
from forms import *
import csv

from django.forms.models import modelformset_factory

def index(request): 
    return render_to_response( 'index.html', RequestContext(request,{'thankyou': False, 'active':'home'}))

def events(request, submit=False): 
    qs = Event.objects.filter()
    result = []
    for event in qs.all(): 
        event_details = {}
        event_details['date'] = event.cleanupdate.strftime('%m/%d/%Y')
        proj = event.proj_id
        orgs = ProjectOrganization.objects.filter(project_id = proj.id)
        lead_org = orgs.filter(is_lead=True)
        if lead_org.count() == 1:
            event_details['org'] = lead_org[0]
        else:
            event_details['org'] = orgs[0]
        org = Organization.objects.filter()
        event_details['event'] = event
        result.append({'event_details':event_details})
            
    return render_to_response( 'events.html', RequestContext(request,{'result':result, 'submit':submit, 'active':'events'}))

@login_required
def create_event(request):
    if request.method == 'GET':
        form = CreateEventForm()
        form.fields['state'].widget = form.fields['state'].hidden_widget()
        form.fields['county'].widget = form.fields['county'].hidden_widget()
        form.fields['site_name'].widget = form.fields['site_name'].hidden_widget()
        form.fields['latitude'].widget = form.fields['latitude'].hidden_widget()
        form.fields['longitude'].widget = form.fields['longitude'].hidden_widget()

        #TODO: Filter Organizations by only those which the user has access to.
        org_dict = [org.toDict for org in Organization.objects.all()]
        org_json = simplejson.dumps(org_dict)
        
        return render_to_response('create_event.html', RequestContext(request,{'form':form.as_p(), 'json':org_json, 'active':'events'}))
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
            event['data_sheet'] = form.data['data_sheet']
            
            datasheet = DataSheet.objects.get(sheetname=event['data_sheet'])
            sites = []
            sitenames = []
            if datasheet.type_id and not datasheet.type_id.display_sites:
                form.fields['site_name'].widget = form.fields['site_name'].hidden_widget()
                form.fields['county'].widget = form.fields['county'].hidden_widget()
            else:
                for site in Site.objects.all().exclude(sitename=''):
                    sites.append({'name':site.sitename, 'lat':site.lat, 'lon':site.lon})
                    sitenames.append(str(site.sitename))

            print sitenames
            
            return render_to_response('event_location.html', RequestContext(request, {'form':form.as_p(), 'event': event, 'sites':sites, 'sitenames': sitenames, 'active':'events'}))
        else:
            res = render_to_response('create_event.html', RequestContext(request,{'form':form.as_p(), 'error':'Form is not valid, please review.', 'active':'events'}))
            res.status_code = 400
            return res

@login_required            
def event_location(request):
    createEventForm = CreateEventForm
    eventForm = createEventForm(request.POST)
    event = {}
    event['organization'] = eventForm.data['organization']
    event['project'] = eventForm.data['project']
    event['date'] = eventForm.data['date']
    event['data_sheet'] = eventForm.data['data_sheet']
    site_check = eventForm.validate_site()
    if site_check['valid']:        #TODO: Manage new sites here!
        for item in eventForm.fields.items():
            eventForm.fields[item[0]].widget = eventForm.fields[item[0]].hidden_widget()
        datasheet_name = eventForm.data['data_sheet']
        datasheet = DataSheet.objects.get(sheetname=datasheet_name)
        if datasheet.type_id and datasheet.type_id.display_sites:
            event['site_name'] = eventForm.data['site_name']
            event['county'] = eventForm.data['county']
        event['state'] = eventForm.data['state']
        event['latitude'] = eventForm.data['latitude']
        event['longitude'] = eventForm.data['longitude']
        form = DataSheetForm(datasheet, None)
    
        return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p(), 'eventForm': eventForm.as_p(), 'event':event, 'active':'events'}))
    else :
        eventForm.fields['organization'].widget = eventForm.fields['organization'].hidden_widget()
        eventForm.fields['project'].widget = eventForm.fields['project'].hidden_widget()
        eventForm.fields['date'].widget = eventForm.fields['date'].hidden_widget()
        eventForm.fields['data_sheet'].widget = eventForm.fields['data_sheet'].hidden_widget()
        return render_to_response('event_location.html', RequestContext(request, {'form': eventForm.as_p(), 'event':event, 'active': 'events', 'error': 'There is an error in your location data. Please be sure to fill out all required fields.'}))

@login_required
def event_save(request):
    createEventForm = CreateEventForm(request.POST)
    if createEventForm.is_valid():
        project = Project.objects.get(projname=createEventForm.data['project'])
        datasheet = DataSheet.objects.get(sheetname=createEventForm.data['data_sheet'])
        state = State.objects.get(initials=createEventForm.data['state'])
        site = Site.objects.get_or_create(state = state, county = createEventForm.data['county'], lat = createEventForm.data['latitude'], lon = createEventForm.data['longitude'], sitename = createEventForm.data['site_name'])
        date = datetime.datetime.strptime(createEventForm.data['date'], '%m/%d/%Y')
        event = Event(proj_id = project, datasheet_id = datasheet, cleanupdate = date, site = site[0])
        event.save()
        if event.id:
            datasheetForm = DataSheetForm(event.datasheet_id, event, request.POST)
        if event.id and datasheetForm.is_valid():
            datasheetForm.save()
            return HttpResponseRedirect('/events/True')
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
            event['site_name'] = createEventForm.data['site_name']
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
    site = Site.objects.get(id=event.site.id)
    values = FieldValue.objects.filter(event_id=event_id)
    fields = []
    for value in values:
        field_name = Field.objects.get(id=value.field_id.id).internal_name
        field = (field_name, value.field_value)
        fields.append(field)
    return render_to_response('view_event.html', RequestContext(request,{'event':event, 'site':site, 'fields':fields, 'active':'events'}))
    
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
        form = DataSheetForm(event.datasheet_id, event)
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
            event_details['site_name'] = event.site.sitename
        return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p(), 'eventForm': None, 'event': event_details, 'action': '/datasheet/edit/'+str(event_id), 'active': 'events'}))
    else:
        datasheetForm = DataSheetForm
        form = datasheetForm(event.datasheet_id, event, request.POST)
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
            event_details['site_name'] = event.site.sitename
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

@login_required    
def bulk_import(request):
    if request.method == 'GET':
        form = BulkImportForm() # instance=ds)
    else:
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

            errors = []

            # confirm required columns
            for i, row in enumerate(rows):
                keys = row.keys()
                for rf in ds.required_fieldnames:
                    if rf not in keys or row[rf] is None:
                        errors.append("Uploaded file does not contain required column '%s'" % (rf,))
                for key in keys:
                    if key not in ds.fieldnames:
                        errors.append("Uploaded file contains column '%s' which is not recognized by this datasheet" % (key,))
                if len(errors) > 0:
                    # return at the datasheet level
                    return bulk_bad_request(form, request, errors)

            # loop through rows and validate against forms
            # also collect sites
            unique_site_keys = []
            for i, row in enumerate(rows):
                row_qnum = {} # keys must refer to the question number (ie 'question_768') 
                for k,v in row.items():
                    dsf = ds.datasheetfield_set.get(field_name=k) 
                    row_qnum['question_%d' % dsf.id] = v

                qd = QueryDict('')
                qd = qd.copy() # to make it mutable
                qd.update(row_qnum)

                ds_form = DataSheetForm(ds, None, qd) #row_qnum)
                
                if not ds_form.is_valid():
                    for question, message in ds_form.errors.items():
                        fieldnum = int(question.replace("question_",''))
                        fieldname = ds.datasheetfield_set.get(pk=fieldnum).field_name
                        errors.append("Row %d, '%s' is invalid: %s" % (i+1, fieldname, message.as_text()))
              
                # TODO derelict gear....TODO instead of cleanup, look at event type
                sitename = settings.REQUIRED_FIELDS['cleanup']['sitename']
                dsf = DataSheetField.objects.get(field_id__internal_name=sitename)
                if row[dsf.field_name] not in unique_site_keys:
                    unique_site_keys.append(row[dsf.field_name])
            
            if len(errors) > 0:
                return bulk_bad_request(form, request, errors)

            sites = []
            for site_key in unique_site_keys:
                # TODO site unique site key should include state and county
                try:
                    site = Site.objects.get(sitename=site_key)
                    sites.append({'name':site_key, 'site':site})
                except:
                    sites.append({'name':site_key, 'site':None})

            # do i need to create an event first? 
            # OR if it's good with unknown sites, store in temp and provide a way to correct site errors  
            # OR if it's good - store in temp and provide a summary with a 'Proceed button'
            #return HttpResponse("valid response")
            return render_to_response('bulk_import_valid.html', RequestContext(request,{'form':form.as_p(), 
                'sites': sites, 'active':'events'}))
        else:
            res = render_to_response('bulk_import.html', RequestContext(request,{'form':form.as_p(), 
                'errors':['Form is not valid, please review.',], 'active':'events'}))
            res.status_code = 400
            return res

    #TODO: Filter Organizations by only those which the user has access to.
    org_dict = [org.toDict for org in Organization.objects.all()]
    org_json = simplejson.dumps(org_dict)
    return render_to_response('bulk_import.html', RequestContext(request,{'form':form.as_p(), 'json':org_json, 'active':'events'}))
