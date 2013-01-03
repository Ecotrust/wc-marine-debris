from django import forms
from models import *
from django.forms.util import ValidationError
from django.forms.util import ErrorList
import re, datetime
from django.forms import TextInput, Textarea
from django.contrib.gis.geos import Point
from cgi import escape
from core import widgets
import datetime

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('id', 'proj_id', 'cleanupdate', 'datasheet_id', 'site')
        widgets = {
            'cleanupdate': TextInput()
        }


class BulkImportForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BulkImportForm, self).__init__(*args, **kwargs)
        
        org_choices = []
        for org in Organization.objects.all():
            org_choices.append((org, org.orgname))
        proj_choices = []
        for proj in Project.objects.all():
            proj_choices.append((proj, proj.projname))
        ds_choices = []
        for ds in DataSheet.objects.all():
            ds_choices.append((ds.id, ds.created_by.orgname + ' ' + str(ds.year_started) + ' ' + ds.sheetname))
            
        self.fields['organization'] = forms.ChoiceField(
            choices = org_choices, 
            widget = widgets.SelectWithTooltip(
                attrs={
                    'data-bind':'options: data.orgs ? data.orgs : [], optionsText: "name", value: selectedOrganizationName, optionsValue: "name", optionsCaption: "Choose..."',
                    'tool-id': 'organization',
                    'tool-title': 'Which organization are these events associated with?',
                    'tool-rel': 'tooltip',
                    'tool-data-placement': 'right'
                }
            )
        )

        self.fields['project'] = forms.ChoiceField(
            choices = proj_choices,
            widget = widgets.SelectWithTooltip(attrs={
                'data-bind':'options: selectedOrganization() ? selectedOrganization().projects : [], optionsText: "name", optionsValue: "name", value: selectedProjectName, optionsCaption: "Select...", enable: selectedOrganizationName',
                'tool-id': 'project',
                'tool-title': 'Which project are these events associated with?',
                'tool-rel': 'tooltip',
                'tool-data-placement': 'right'
            })
        )

        self.fields['datasheet'] = forms.ChoiceField(
            choices = ds_choices,
            widget = widgets.SelectWithTooltip(attrs={
                'data-bind':'options: availableDatasheets() ? availableDatasheets() : [], optionsText: "name", value: selectedDatasheet, optionsCaption: "Select...", optionsValue: "id", enable: availableDatasheets',
                'tool-id': 'datasheet',
                'tool-title': 'Which data sheet matches the fields on the CSV that you wish to upload?',
                'tool-rel': 'tooltip',
                'tool-data-placement': 'right'
            })
        )
        
        self.fields['csv_file'] = forms.FileField(
            widget = widgets.FileFieldWithTooltip(attrs={
                'tool-id': 'csv',
                'tool-title': 'Browse to and select the Comma Separated Value file that contains the events data.',
                'tool-rel': 'tooltip',
                'tool-data-placement': 'right'
            })
        )
        
class CreateEventForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(CreateEventForm, self).__init__(*args, **kwargs)

        org_choices = []
        for org in Organization.objects.all():
            org_choices.append((org, org.orgname))
        proj_choices = []
        for proj in Project.objects.all():
            proj_choices.append((proj, proj.projname))
        ds_choices = []
        for ds in DataSheet.objects.all():
            ds_choices.append((ds.id, ds.created_by.orgname + ' ' + str(ds.year_started) + ' ' + ds.sheetname))
            
        self.fields['organization'] = forms.ChoiceField(
            choices = org_choices, 
            widget = widgets.SelectWithTooltip(
                attrs={
                    'data-bind':'options: data.orgs ? data.orgs : [], optionsText: "name", value: selectedOrganizationName, optionsValue: "name", optionsCaption: "Choose..."',
                    'tool-id': 'organization',
                    'tool-rel': 'tooltip',
                    'tool-data-placement': 'right',
                    'tool-title': 'Which organization is this event associated with? Only organizations that you are associated with will be shown here. If the options seem incorrect, please contact your project lead or organization contact and request to have your account associated with the correct '
                }
            )
        )
        self.fields['project'] = forms.ChoiceField(
            choices = proj_choices,
            widget = widgets.SelectWithTooltip(
                attrs={
                    'data-bind':'options: selectedOrganization() ? selectedOrganization().projects : [], optionsText: "name", optionsValue: "name", value: selectedProjectName, optionsCaption: "Select...", enable: selectedOrganizationName',
                    'tool-id' : 'project',
                    'tool-rel': 'tooltip',
                    'tool-data-placement': 'right',
                    'tool-title': 'Which project was this event performed for? Only projects associated with the organization you selected in the previous field will be shown.',
                }
            )
        )
        self.fields['date'] = forms.DateField(
            widget=widgets.TextInputWithTooltip(
                attrs={
                    'class':'date', 
                    'data-bind':'datepicker: selectedDate, enable: selectedProjectName',
                    'tool-id': 'date',
                    'tool-rel': 'tooltip',
                    'tool-data-placement': 'right',
                    'tool-title': 'The date on which the event occurred. For cleanups this would be the first day of the cleanup. For derelict gear reports/removals it would be the day that the derelict gear was reported.' 
                }
            )
        )
        self.fields['data_sheet'] = forms.ChoiceField(
            choices = ds_choices,
            widget = widgets.SelectWithTooltip(
                attrs={
                    'data-bind':'options: availableDatasheets() ? availableDatasheets() : [], optionsText: "name", value: selectedDatasheet, optionsCaption: "Select...", optionsValue: "id", enable: availableDatasheets',
                    'tool-id': 'data_sheet',
                    'tool-title': 'Which data sheet was used to collect the data? Datasheets are the list of questions used for reporting your event.',
                    'tool-rel': 'tooltip',
                    'tool-data-placement': 'right'
                }
            )
        )
        state_choices = []
        for state in State.objects.all():
            state_choices.append((state.initials, state.name))
        county_choices = []
        for county in County.objects.all():
            county_choices.append((county.name, county.name))
        site_choices = []
        if settings.DEMO:
            sites = Site.objects.all().exclude(sitename='')
        else:
            sites = Site.objects.filter(transaction__status = "accepted").exclude(sitename='')
        for site in sites:
            site_choices.append(escape('"' + str(site.sitename) + '"'))
        
        self.fields['state'] = forms.ChoiceField(
            choices = state_choices, 
            required=False,
            widget = widgets.SelectWithTooltip(
                attrs={
                    'class':'state-select',
                    'data-bind':'options: data.states ? data.states : [], optionsText: "name", value: selectedStateName, optionsValue: "initials", optionsCaption: "Choose..."',
                    'tool-id': 'state',
                    'tool-title': 'Which state (waters) was this event performed in?',
                    'tool-rel': 'tooltip',
                    'tool-data-placement': 'right'
                }
            )
        )
        self.fields['county'] = forms.ChoiceField(
            choices = county_choices,
            required=False,
            widget = widgets.SelectWithTooltip(
                attrs={
                    'class':'county-select',
                    'data-bind':'options: selectedState().counties ? selectedState().counties.sort(function(a, b) { return a.name.localeCompare(b.name) }) : [], optionsText: "name", value: selectedCountyName, optionsValue: "name", optionsCaption: "Choose...", enable: selectedState',
                    'tool-id': 'county',
                    'tool-title': 'Which county (waters) was this event performed in?',
                    'tool-rel': 'tooltip',
                    'tool-data-placement': 'right'
                }
            )
        )
        self.fields['sitename'] = forms.CharField(
            required=False,
            widget = widgets.TextInputWithTooltip(
                attrs={
                    'class':'site-typeahead',
                    'autocomplete':'off',
                    'data-bind':'value: selectedSiteName, enable: selectedCounty',
                    'tool-id': 'sitename',
                    'tool-title': 'What is the name of the site where this event was performed? Feel free to select from the options suggested. If your site\'s name isn\'t in the list, you may use what you typed.',
                    'tool-rel': 'tooltip',
                    'tool-data-placement': 'right'
                }
            )
        )
        self.fields['longitude'] = forms.CharField(
            label="Longitude (or click on map)",
            required=False,
            widget = widgets.TextInputWithTooltip(
                attrs={
                    'data-bind': 'enable: selectedState, value: longitude',
                    'tool-id': 'longitude',
                    'tool-title': 'What was the approximate longitude of the site where your event was performed? This can be filled in by either selecting a pre-existing site name above, or by clicking on the map below.',
                    'tool-rel': 'tooltip',
                    'tool-data-placement': 'right'
                }
            )
        )
        self.fields['latitude'] = forms.CharField(
            label="Latitude (or click on map)",
            required=False,
            widget = widgets.TextInputWithTooltip(
                attrs={
                    'data-bind': 'enable: selectedState, value: latitude',
                    'tool-id': 'latitude',
                    'tool-title': 'What was the approximate latitude of the site where your event was performed? This can be filled in by either selecting a pre-existing site name above, or by clicking on the map below.',
                    'tool-rel': 'tooltip',
                    'tool-data-placement': 'right'
                }
            )
        )
    
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
                            if str(record.geometry.get_coords()[1]) == self.data['latitude'] and str(record.geometry.get_coords()[0]) == self.data['longitude'] and (record.county == self.data['county'] or record.county == self.data['county']+' County') and record.state.initials == self.data['state']:
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
        
    def validate_unique(self, *args, **kwargs):
        valid = True
        error = None
        datasheet = DataSheet.objects.get(id = self.data['data_sheet'])
        if datasheet.type_id.display_sites:
            state = State.objects.get(initials = self.data['state'])
            sites = Site.objects.filter(sitename = self.data['sitename'], county = self.data['county'], state = state)
        else:
            point = Point(float(self.data['longitude']), float(self.data['latitude']))
            sites = Site.objects.filter(geometry = point)
        if sites.__len__() > 0:
            for site in sites:
                date = datetime.datetime.date(datetime.datetime.strptime(self.data['date'], "%m/%d/%Y"))
                project = Project.objects.get(projname = self.data['project'])
                dupes = Event.objects.filter(cleanupdate = date, proj_id = project, site = site, datasheet_id = datasheet)
                if dupes.__len__() > 0:
                    error = 'An event for this project, date, location, and datasheet already exists! Please do not enter duplicate data.'
                    valid = False
        return {'valid': valid, 'error': error}
    
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
                        dynamic_args['initial'] = datetime.datetime.date(datetime.datetime.strptime(answer, "%Y-%m-%d"))
                    elif field.default_value  != '':
                        dynamic_args['initial'] = datetime.datetime.date(datetime.datetime.strptime(field.default_value, "%Y-%m-%d"))
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

    def hideRequiredFields(self, datasheet):
        for key in self.fields:
            field = self.fields[key]
            if field.field.internal_name in settings.REQUIRED_FIELDS[datasheet.site_type].values():
                field.widget = field.hidden_widget()
        
    def save(self, datasheet):
        now = datetime.datetime.today()
        for field_name in self.fields:
            fld = self.fields[field_name]
            if not fld.field.internal_name in settings.REQUIRED_FIELDS[datasheet.site_type].values():     #Do Not Save Values for required ('event level') fields
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
