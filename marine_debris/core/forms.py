from django import forms
from models import *
from django.forms.util import ValidationError
from django.forms.util import ErrorList
import re, datetime
from django.forms import TextInput, Textarea

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('id', 'proj_id', 'cleanupdate', 'datasheet_id', 'site')
        widgets = {
            'cleanupdate': TextInput()
        }
        
class CreateEventForm(forms.Form):
    org_choices = []
    for org in Organization.objects.all():
        org_choices.append((org, org.orgname))
    proj_choices = []
    for proj in Project.objects.all():
        proj_choices.append((proj, proj.projname))
    ds_choices = []
    for ds in DataSheet.objects.all():
        ds_choices.append((ds, ds.sheetname))
        
    organization = forms.ChoiceField(
        choices = org_choices, 
        widget = forms.Select(attrs={'class': 'span6', 'data-bind':'options: data.orgs, optionsText: "name", value: selectedOrganization, optionsCaption: "Choose..."'})
    )
    project = forms.ChoiceField(
        choices = proj_choices,
        widget = forms.Select(attrs={'data-bind':'options: selectedOrganization() ? selectedOrganization().projects : [], optionsText: "name", value: selectedProject, optionsCaption: "Select...", enable: selectedOrganization'})
    )
    date = forms.DateField(
        widget=forms.TextInput(attrs={'class':'date', 'data-bind':'datepicker: selectedDate, enable: selectedProject'}))
    data_sheet = forms.ChoiceField(
        choices = ds_choices,
        widget = forms.Select(attrs={'data-bind':'options: availableDatasheets() ? availableDatasheets() : [], optionsText: "name", value: selectedDatasheet, optionsCaption: "Select...", enable: availableDatasheets'})
    )
    
    state_choices = []
    for state in State.objects.all():
        state_choices.append((state.initials, state.name))
    site_choices = [(None, 'Select a site')]
    for site in Site.objects.all().exclude(sitename=''):
        site_choices.append((site.sitename, site.sitename))
    
    state = forms.ChoiceField(state_choices, required=False)
    county = forms.CharField(required=False)
    site_name = forms.ChoiceField(site_choices, required=False)
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
                datasheet = DataSheet.objects.get(sheetname = self.data['data_sheet'])
                if datasheet.type_id.display_sites: 
                    if self.data['site_name'].__len__() > 0:    #site will have name, and name is given
                        records = Site.objects.filter(sitename=self.data['site_name'])
                        for record in records:
                            if str(record.lat) == self.data['latitude'] and str(record.lon) == self.data['longitude'] and record.county == self.data['county'] and record.state.initials == self.data['state']:
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
    def __init__(self, datasheet, event=None, *args, **kwargs):
        self.datasheet_id = datasheet.id
        questions = DataSheetField.objects.filter(sheet_id=datasheet.id)
        if event:
            answers = FieldValue.objects.filter(event_id=event.id)
        else:
            answers = FieldValue.objects.none()
        self.answers = answers
        forms.Form.__init__(self, *args, **kwargs)
            
        for i, question in enumerate(questions):
            dynamic_args = {}
            other_dynamic_args = {}
            field = Field.objects.get(id = question.field_id.id)
            dynamic_args['label'] = question.print_name
            dynamic_args['required']=question.required
            answer = answers.filter(field_id = question.field_id.id)
            
            if question.field_id.datatype.name == 'Area' or question.field_id.datatype.name == 'Distance' or question.field_id.datatype.name == 'Duration' or question.field_id.datatype.name == 'Number' or question.field_id.datatype.name == 'Volume' or question.field_id.datatype.name == 'Weight': # decimal
                if question.field_id.minvalue != None:
                    dynamic_args['min_value']=int(question.field_id.minvalue)
                if question.field_id.maxvalue != None:
                    dynamic_args['max_value']=int(question.field_id.maxvalue)
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=int(question.field_id.default_value)
                self.fields['question_' + str(question.id)] = forms.FloatField( **dynamic_args )
                
            elif question.field_id.datatype.name == 'True/False':
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=bool(question.field_id.default_value)
                dynamic_args['required'] = False
                self.fields['question_' + str(question.id)] = forms.BooleanField( **dynamic_args )
                
            elif question.field_id.datatype.name == 'Date':
                if answer.count() == 1:
                    try:
                        dynamic_args['initial']=datetime.datetime.strptime(answer[0].field_value, "%Y-%m-%d %H:%M:%S.%f")
                    except: 
                        try:
                            dynamic_args['initial']=datetime.datetime.strptime(answer[0].field_value, "%Y-%m-%d %H:%M:%S")
                        except:
                            dynamic_args['initial']=datetime.datetime.strptime(answer[0].field_value, "%Y-%m-%d")
                elif question.field_id.default_value  != '':
                    try:
                        dynamic_args['initial']=datetime.datetime.strptime(question.field_id.default_value, "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        try:
                            dynamic_args['initial']=datetime.datetime.strptime(question.field_id.default_value, "%Y-%m-%d %H:%M:%S")
                        except:
                            dynamic_args['initial']=datetime.datetime.strptime(question.field_id.default_value, "%Y-%m-%d")
                else:
                    dynamic_args['initial']=datetime.datetime.now()
                dynamic_args['widget']=forms.TextInput(attrs={'class':'date'})
                self.fields['question_' + str(question.id)] = forms.CharField( **dynamic_args )
                
                # elif question.field_id.datatype.name == 'Location':
            
            elif question.field_id.datatype.name == 'Yes/No':
                options = (('yes', 'Yes'), ('no', 'No'))
                dynamic_args['choices'] = options
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=question.field_id.default_value
                self.fields['question_' + str(question.id)] = forms.ChoiceField( **dynamic_args )
            
            # elif question.field_id.datatype.name == 'Text' or question.field_id.datatype.name == 'Location' or question.field_id.datatype.name == 'Other':
            else:
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=question.field_id.default_value
                self.fields['question_' + str(question.id)] = forms.CharField( **dynamic_args )

            self.fields['question_' + str(question.id)].question = question
            self.fields['question_' + str(question.id)].answer = answer
            self.fields['question_' + str(question.id)].event = event
            
    def save(self):
        for field_name in self.fields:
            field = self.fields[field_name]
            answer = self.cleaned_data[field_name]
            value = FieldValue.objects.get_or_create(event_id=field.event, field_id=field.question.field_id)[0]
            value.field_value=str(answer)
            value.last_modified = datetime.datetime.today()
            value.save()
        return True
           