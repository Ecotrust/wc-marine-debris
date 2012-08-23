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
    form = EventForm()
    # EventFormSet = modelformset_factory(Event)
    # form = EventFormSet()
    return render_to_response('create_event.html', RequestContext(request,{'form':form}))
    
# @login_required    
def edit_event(request, event_id):
    event = Event.objects.get(id=event_id)
    return render_to_response( 'edit_event.html', RequestContext(request,{'event':event}))
    
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