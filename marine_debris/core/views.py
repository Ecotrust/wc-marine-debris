from django import template
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.views import login as default_login, logout as default_logout
import datetime
import string
import simplejson
import datetime
from forms import *

from django.forms.models import modelformset_factory

# @login_required
def index(request): 
    return render_to_response( 'index.html', RequestContext(request,{'active':'home'}))

# @login_required
def events(request): 
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
            
    return render_to_response( 'events.html', RequestContext(request,{'result':result, 'active':'events'}))
    
@login_required
def create_event(request):
    if request.method == 'GET':
        form = CreateEventForm()
        #TODO: make dummy location objects here
        return render_to_response('create_event.html', RequestContext(request,{'form':form.as_p(), 'active':'events'}))
    else :
        #TODO: move to get location
        eventForm = CreateEventForm
        form = eventForm(request.POST)
        if form.is_valid():
            # import pdb
            # pdb.set_trace()
            organization = form.data['organization']
            new_event = {'proj_id': form.data['project'], 'cleanupdate': form.data['date'], 'datasheet_id': form.data['data_sheet'], 'state':form.data['state']}
            #TODO: create location form, pass it in RequestContext
            
            # return render_to_response('create_event.html', RequestContext(request,{'event':new_event, 'form':form.as_p(), 'active':'events'}))
            # return HttpResponseRedirect('/datasheet/fill/'+datasheet_id+'/'+str(new_event.id))
            return HttpResponseRedirect('/event/location')
        else:
            return render_to_response('create_event.html', RequestContext(request,{'form':form.as_p(), 'error':'Form is not valid, please review.', 'active':'events'}))
            

@login_required            
def event_location(request):
    # import pdb
    # pdb.set_trace()
    if request.method == 'GET':
        loc_form = EventLocationForm()
        #TODO: This is dummy data - learn to create and save data from create_event view (django session? cookies?) and bring it here.
        # organization = form.data['organization']
        organization = 'Coast Savers'
        # new_event = {'proj_id': form.data['project'], 'cleanupdate': form.data['date'], 'datasheet_id': form.data['data_sheet'], 'state':form.data['state']}
        new_event = {'proj_id': 'Beach Cleanups', 'cleanupdate': '2012-09-05', 'datasheet_id': DataSheet.objects.get(sheetname='2009 ODFW Derelict Fishing Gear'), 'state':'CA'}
        return render_to_response('event_location.html', RequestContext(request, {'form': loc_form, 'organization': organization, 'event':new_event, 'active':'events'}))
    else:
        #TODO: Populate an Event ModelForm and save it - capture the id to pass in the response redirect.
        # event_form = EventForm()
        # event_form.fields['proj_id'].initial = 'Beach Cleanups'
        # event_form.fields['cleanupdate'].initial = '2012-09-05'
        # event_form.fields['datasheet_id'].initial = DataSheet.objects.get(sheetname='2009 ODFW Derelict Fishing Gear')
        # event_form.fields['state'].initial = 'CA'
        # event_form.fields['sitename'].initial = form.data['site_name']
        # event_form.fields['city'].initial = 'city'
        # event_form.fields['county'].initial = 'county'
        # event_form.fields['lat'].initial = form.data['latitude']
        # event_form.fields['lon'].initial = form.data['longitude']
        # 'proj_id', 'cleanupdate', 'datasheet_id', 'sitename', 'city', 'state', 'county', 'lat', 'lon'
        # event = event_form.save()
        # datasheet = DataSheet.objects.get(id=event.datasheet_id)
        event = Event.objects.all()[0]
        datasheet = DataSheet.objects.all()[4]
        return HttpResponseRedirect('/datasheet/fill/'+str(event.id))
        
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
                return HttpResponseRedirect('/datasheet/fill/'+event_id)
            return HttpResponseRedirect('/events')
        else:
            return render_to_response( 'edit_event.html', RequestContext(request,{'event':event, 'form':form.as_p(), 'error':'Form is not valid, please review.', 'active':'events'}))
    return render_to_response( 'edit_event.html', RequestContext(request,{'event':event, 'form':form.as_p(), 'active':'events'}))
    
# @login_required
def view_event(request, event_id):
    event = Event.objects.get(id=event_id)
    values = FieldValue.objects.filter(event_id=event_id)
    fields = []
    for value in values:
        field_name = Field.objects.get(id=value.field_id.id).internal_name
        field = (field_name, value.field_value)
        fields.append(field)
    return render_to_response('view_event.html', RequestContext(request,{'event':event, 'fields':fields, 'active':'events'}))
    
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
def fill_datasheet(request, event_id):
    #TODO: add organization to be displayed
    event = Event.objects.get(id=event_id)
    if request.method == 'GET':
        organization = 'Coast Savers'
        date = event.cleanupdate.date()
        form = DataSheetForm(event)
        return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p(), 'organization': organization, 'event':event, 'date':date, 'active':'datasheets'}))
    else:
        datasheetForm = DataSheetForm
        form = datasheetForm(event, request.POST)
        if form.is_valid():
            new_datasheet = form.save()
            return HttpResponseRedirect('/events')
        else:
            return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p(), 'error': 'Form is not valid, please review.', 'active':'datasheets'}))
    
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