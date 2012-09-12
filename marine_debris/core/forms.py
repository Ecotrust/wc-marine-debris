from django import forms
from models import *
from django.forms.util import ValidationError
from django.forms.util import ErrorList
import re, datetime
from django.forms import TextInput, Textarea

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('id', 'proj_id', 'cleanupdate', 'datasheet_id', 'sitename', 'city', 'state', 'county', 'lat', 'lon')
        widgets = {
            'cleanupdate': TextInput(),
            'sitename': TextInput(),
            'city': TextInput(),
            'county': TextInput(),
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
    state_choices = []
    for state in State.objects.all():
        state_choices.append((state.initials, state.name))
    organization = forms.ChoiceField(org_choices)
    project = forms.ChoiceField(proj_choices)
    date = forms.DateField(
        widget=forms.TextInput(attrs={'class':'date'}))
    data_sheet = forms.ChoiceField(ds_choices)
    state = forms.ChoiceField(state_choices)
    
    def save(self):
        #TODO: either store this temporarily or create the event if possible
        return True
        
class EventLocationForm(forms.Form):
    site_choices = [
        ('Twin Lakes State Beach', 'Twin Lakes State Beach'),
        ('Cowell Beach', 'Cowell Beach'),
        ('Hidden Beach', 'Hidden Beach'),
        ('Seacliff State Beach', 'Seacliff State Beach')
    ]
    format_choices = [
        ('Decimal Degrees', 'DD.dddd, -DDD.dddd'),
        ('Degrees Minutes Seconds Compass', 'DD MM\'SS"C and DD MM\'SS"C')
    ]
    site_name = forms.ChoiceField(site_choices)
    format = forms.ChoiceField(format_choices)
    latitude = forms.CharField()
    longitude = forms.CharField()
        
class DataSheetForm(forms.Form):
    def __init__(self, datasheet_id, event_id, *args, **kwargs):
        self.datasheet_id = datasheet_id
        questions = DataSheetField.objects.filter(sheet_id=datasheet_id)
        self.event_id = event_id
        answers = FieldValue.objects.filter(event_id=event_id)
        event = Event.objects.get(id=event_id)
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
                self.fields['question_' + str(question.id) + '_' + self.event_id] = forms.FloatField( **dynamic_args )
                
            elif question.field_id.datatype.name == 'True/False':
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=bool(question.field_id.default_value)
                dynamic_args['required'] = False
                self.fields['question_' + str(question.id) + '_' + self.event_id] = forms.BooleanField( **dynamic_args )
                
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
                self.fields['question_' + str(question.id) + '_' + self.event_id] = forms.CharField( **dynamic_args )
                
                # elif question.field_id.datatype.name == 'Location':
            
            elif question.field_id.datatype.name == 'Yes/No':
                options = (('yes', 'Yes'), ('no', 'No'))
                dynamic_args['choices'] = options
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=question.field_id.default_value
                self.fields['question_' + str(question.id) + '_' + self.event_id] = forms.ChoiceField( **dynamic_args )
            
            # elif question.field_id.datatype.name == 'Text' or question.field_id.datatype.name == 'Location' or question.field_id.datatype.name == 'Other':
            else:
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=question.field_id.default_value
                self.fields['question_' + str(question.id) + '_' + self.event_id] = forms.CharField( **dynamic_args )

            self.fields['question_' + str(question.id) + '_' + self.event_id].question = question
            self.fields['question_' + str(question.id) + '_' + self.event_id].answer = answer
            self.fields['question_' + str(question.id) + '_' + self.event_id].event = event
            
    def save(self):
        for field_name in self.fields:
            field = self.fields[field_name]
            answer = self.cleaned_data[field_name]
            value = FieldValue.objects.get_or_create(event_id=field.event, field_id=field.question.field_id)[0]
            value.field_value=str(answer)
            value.last_modified = datetime.datetime.today()
            value.save()
        return True
           