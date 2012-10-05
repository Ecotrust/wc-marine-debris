from django import forms
from models import *
from django.forms.util import ValidationError
from django.forms.util import ErrorList
import re, datetime
from django.forms import TextInput, Textarea
from cgi import escape

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('id', 'proj_id', 'cleanupdate', 'datasheet_id', 'site')
        widgets = {
            'cleanupdate': TextInput()
        }


class BulkImportForm(forms.Form):
    org_choices = []
    for org in Organization.objects.all():
        org_choices.append((org, org.orgname))
    proj_choices = []
    for proj in Project.objects.all():
        proj_choices.append((proj.id, proj.projname))
    ds_choices = []
    for ds in DataSheet.objects.all():
        ds_choices.append((ds.id, ds.sheetname))
        
    organization = forms.ChoiceField(
        choices = org_choices, 
        widget = forms.Select()
    )
    project_id = forms.ChoiceField(
        choices = proj_choices,
        widget = forms.Select()
    )
    datasheet_id = forms.ChoiceField(
        choices = ds_choices,
        widget = forms.Select()
    )
    
    csvfile = forms.FileField()
        
class CreateEventForm(forms.Form):
    org_choices = []
    for org in Organization.objects.all():
        org_choices.append((org, org.orgname))
    proj_choices = []
    for proj in Project.objects.all():
        proj_choices.append((proj, proj.projname))
    ds_choices = []
    for ds in DataSheet.objects.all():
        ds_choices.append((ds.id, ds.sheetname))
        
    organization = forms.ChoiceField(
        choices = org_choices, 
        widget = forms.Select(
            attrs={
                'class': 'span6', 
                'data-bind':'options: data.orgs ? data.orgs : [], optionsText: "name", value: selectedOrganizationName, optionsValue: "name", optionsCaption: "Choose..."'
            }
        )
    )
    project = forms.ChoiceField(
        choices = proj_choices,
        widget = forms.Select(
            attrs={
                'data-bind':'options: selectedOrganization() ? selectedOrganization().projects : [], optionsText: "name", optionsValue: "name", value: selectedProjectName, optionsCaption: "Select...", enable: selectedOrganizationName'
            }
        )
    )
    date = forms.DateField(
        widget=forms.TextInput(
            attrs={
                'class':'date', 
                'data-bind':'datepicker: selectedDate, enable: selectedProjectName'
            }
        )
    )
    data_sheet = forms.ChoiceField(
        choices = ds_choices,
        widget = forms.Select(
            attrs={
                'data-bind':'options: availableDatasheets() ? availableDatasheets() : [], optionsText: "name", value: selectedDatasheet, optionsCaption: "Select...", optionsValue: "id", enable: availableDatasheets'
            }
        )
    )
    state_choices = []
    for state in State.objects.all():
        state_choices.append((state.initials, state.name))
    site_choices = []
    for site in Site.objects.all().exclude(sitename=''):
        site_choices.append(escape('"' + str(site.sitename) + '"'))
    
    state = forms.ChoiceField(
        choices = state_choices, 
        required=False,
        widget = forms.Select(
            attrs={
            'class':'span6',
            'data-bind':'options: data.states ? data.states : [], optionsText: "name", value: selectedStateName, optionsValue: "initials", optionsCaption: "Choose..."'
            }
        )
    )
    county = forms.CharField(
        required=False,
        widget = forms.TextInput(
            attrs={
                'class':'county-typeahead',
                'autocomplete':'off',
                'data-bind':'value: selectedCountyName, enable: selectedState'
            }
        )
    )
    sitename = forms.CharField(
        required=False,
        widget = forms.TextInput(
            attrs={
                'class':'site-typeahead',
                'autocomplete':'off',
                'data-bind':'value: selectedSiteName, enable: selectedCounty'
            }
        )
    )
    longitude = forms.CharField(required=False)
    latitude = forms.CharField(required=False)
    
    #Check the event details fields of the form for validity
    def validate_event(self, *args, **kwargs):
        if self.data['organization'].__len__() > 0 and self.data['project'].__len__() > 0 and self.data['date'].__len__() > 0 and self.data['data_sheet'].__len__() > 0:
            return True
        else:
            return False
    
    #Check the site fields of the form for validity
    def validate_site(self, *args, **kwargs):
        valid = False
        exists = False
        matches = []
        error = None
        if self.data['latitude'].__len__() > 0 and self.data['latitude'].__len__() > 0:
            valid = True
        if valid:
            try:
                datasheet = DataSheet.objects.get(id = self.data['data_sheet'])
                if datasheet.type_id.display_sites: 
                    if self.data['sitename'].__len__() > 0:    #site will have name, and name is given
                        records = Site.objects.filter(sitename=self.data['sitename'])
                        for record in records:
                            if str(record.geometry.get_coords()[1]) == self.data['latitude'] and str(record.geometry.get_coords()[0]) == self.data['longitude'] and record.county == self.data['county'] and record.state.name == self.data['state']:
                                matches = [record]
                                exists = True
                                break
                            else:
                                matches.append(record)
                    else:
                        valid = False           #site must have name since this is not a derelict fishing gear event
                        error = 'Site must have a name'
            except:
                valid = False                   #datasheet not found. Not valid.
        return {'valid':valid, 'exists':exists, 'matches':matches, 'error':error}
    
class DataSheetForm(forms.Form):
    def __init__(self, datasheet, event=None, event_post=None, *args, **kwargs):
        self.datasheet_id = datasheet.id
        questions = DataSheetField.objects.select_related().filter(sheet_id=datasheet.id)
        if event:
            answers = FieldValue.objects.filter(event_id=event.id)
        else:
            answers = FieldValue.objects.none()
        forms.Form.__init__(self, *args, **kwargs)

        answer_lookup = dict([(a.field_id, a.field_value) for a in answers.all()])
        field_lookup = dict([(f.id, f) for f in Field.objects.select_related().all()])

        for i, question in enumerate(questions):
            dynamic_args = {}
            other_dynamic_args = {}
            field = question.field_id
                    
            hidden = False
            if question.field_id.internal_name in settings.REQUIRED_FIELDS[datasheet.site_type].values() and event_post:
                hidden = True
                reqflds = settings.REQUIRED_FIELDS[question.sheet_id.site_type]
                key =  [k for k, v in reqflds.items() if v == question.field_id.internal_name][0]
                dynamic_args['initial'] = event_post[key]

            datatype = field.datatype.name
            try:
                answer = answer_lookup[field.id]
            except KeyError:
                answer = None

            if question.print_name and not question.print_name == '':
                dynamic_args['label'] = question.print_name
            else:
                dynamic_args['label'] = question.field_name
                
            dynamic_args['required'] = question.required
            
            if datatype in ['Area', 'Distance', 'Duration', 'Number', 'Volume', 'Weight']: 
                # decimal
                if field.minvalue != None:
                    dynamic_args['min_value'] = int(field.minvalue)
                if field.maxvalue != None:
                    dynamic_args['max_value'] = int(field.maxvalue)
                if not dynamic_args.has_key('initial'):
                    if answer:
                        dynamic_args['initial'] = answer
                    elif field.default_value != '':
                        dynamic_args['initial'] = int(field.default_value)
                self.fields['question_' + str(question.id)] = forms.FloatField( **dynamic_args )
                
            elif datatype == 'True/False':
                if not dynamic_args.has_key('initial'):
                    if answer:
                        dynamic_args['initial'] = answer
                    elif field.default_value != '':
                        dynamic_args['initial'] = bool(field.default_value)
                dynamic_args['required'] = False
                self.fields['question_' + str(question.id)] = forms.BooleanField( **dynamic_args )
                
            elif datatype == 'Date':
                if not dynamic_args.has_key('initial'):
                    if answer:
                        dynamic_args['initial'] = datetime.datetime.strptime(answer, "%Y-%m-%d")
                    elif field.default_value  != '':
                        dynamic_args['initial'] = datetime.datetime.strptime(field.default_value, "%Y-%m-%d")
                dynamic_args['widget'] = forms.TextInput(attrs={'class':'date'})
                self.fields['question_' + str(question.id)] = forms.DateField( **dynamic_args )
            
            elif datatype == 'Yes/No':
                options = (('yes', 'Yes'), ('no', 'No'))
                dynamic_args['choices'] = options
                if not dynamic_args.has_key('initial'):
                    if answer:
                        dynamic_args['initial'] = answer
                    elif field.default_value != '':
                        dynamic_args['initial'] = field.default_value
                self.fields['question_' + str(question.id)] = forms.ChoiceField( **dynamic_args )
            
            else:
                if not dynamic_args.has_key('initial'):
                    if answer:
                        dynamic_args['initial'] = answer
                    elif field.default_value != '':
                        dynamic_args['initial'] = field.default_value
                self.fields['question_' + str(question.id)] = forms.CharField( **dynamic_args )

            self.fields['question_' + str(question.id)].question = question
            self.fields['question_' + str(question.id)].field = field 
            self.fields['question_' + str(question.id)].answer = answer
            self.fields['question_' + str(question.id)].event = event

            if hidden:
                self.fields['question_' + str(question.id)].widget = self.fields['question_' + str(question.id)].hidden_widget()
            
        self.event = event

    def save(self):
        now = datetime.datetime.today()
        for field_name in self.fields:
            fld = self.fields[field_name]
            answer = self.cleaned_data[field_name]
            value = FieldValue.objects.get_or_create(event_id=fld.event, field_id=fld.field)[0]
            value.field_value = unicode(answer)
            value.last_modified = now
            value.save()
        return True
           

class CreateSiteForm(forms.ModelForm):
    county = forms.CharField(required=True,)
    sitename = forms.CharField(required=True,)
    longitude = forms.CharField(required=False)
    latitude = forms.CharField(required=False)
    geometry = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = Site
