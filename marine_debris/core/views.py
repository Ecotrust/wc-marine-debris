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
    return render_to_response( 'index.html', RequestContext(request,{}))

# @login_required
def events(request): 
    qs = Event.objects.filter()
    result = []
    for event in qs.all(): 
        result.append({'event':event})
            
    return render_to_response( 'events.html', RequestContext(request,{'result':result}))
    
# @login_required
def create_event(request):
    if request.method == 'GET':
        form = EventForm()
        return render_to_response('create_event.html', RequestContext(request,{'form':form.as_p()}))
    else :
        eventForm = EventForm
        form = eventForm(request.POST)
        if form.is_valid():
            new_event = form.save()
            datasheet_id = form.data['datasheet_id']
            return HttpResponseRedirect('/datasheet/fill/'+datasheet_id+'/'+str(new_event.id))
        else:
            return render_to_response('create_event.html', RequestContext(request,{'form':form.as_p(), 'error':'Form is not valid, please review.'}))
        
# @login_required    
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
                return HttpResponseRedirect('/datasheet/fill/'+form.data['datasheet_id']+'/'+event_id)
            return HttpResponseRedirect('/events')
        else:
            return render_to_response( 'edit_event.html', RequestContext(request,{'event':event, 'form':form.as_p(), 'error':'Form is not valid, please review.'}))
    return render_to_response( 'edit_event.html', RequestContext(request,{'event':event, 'form':form.as_p()}))
    
# @login_required
def view_event(request, event_id):
    event = Event.objects.get(id=event_id)
    values = FieldValue.objects.filter(event_id=event_id)
    fields = []
    for value in values:
        field_name = Field.objects.get(id=value.field_id.id).internal_name
        field = (field_name, value.field_value)
        fields.append(field)
    return render_to_response('view_event.html', RequestContext(request,{'event':event, 'fields':fields}))
    
# @login_required
def datasheets(request):
    qs = DataSheet.objects.filter()
    result = []
    for datasheet in qs.all():
        result.append({'datasheet': datasheet})
        
    return render_to_response('datasheets.html', RequestContext(request, {'result':result}))
    
# @login_required
def fill_datasheet(request, datasheet_id, event_id):
    if request.method == 'GET':
        form = DataSheetForm(datasheet_id, event_id)
        return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p()}))
    else:
        datasheetForm = DataSheetForm
        form = datasheetForm(datasheet_id, event_id, request.POST)
        if form.is_valid():
            new_datasheet = form.save()
            return HttpResponseRedirect('/')
        else:
            return render_to_response('fill_datasheet.html', RequestContext(request, {'form':form.as_p(), 'error': 'Form is not valid, please review.'}))
    
# @login_required
def organizations(request): 
    qs = Organization.objects.filter()
    result = []
    for organization in qs.all(): 
        result.append({'organization':organization})
            
    return render_to_response( 'organizations.html', RequestContext(request,{'result':result}))

# @login_required
def projects(request): 
    qs = Project.objects.filter()
    result = []
    for project in qs.all(): 
        result.append({'project':project})
            
    return render_to_response( 'projects.html', RequestContext(request,{'result':result}))    