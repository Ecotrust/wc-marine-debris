from django import forms
from models import *
from django.forms.util import ValidationError
from django.forms.util import ErrorList
import re, datetime
from django.forms import TextInput, Textarea

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('proj_id', 'type_id', 'cleanupdate', 'datasheet_id', 'sitename', 'city', 'state', 'county', 'lat', 'lon')
        widgets = {
            'sitename': TextInput(),
            'city': TextInput(),
            'state': TextInput(),
            'county': TextInput(),
        }
        
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
            answer = answers.filter(field_id = question.field_id.id)
            
            if question.field_id.datatype == 'area' or question.field_id.datatype == 'distance' or question.field_id.datatype == 'duration' or question.field_id.datatype == 'number' or question.field_id.datatype == 'volume' or question.field_id.datatype == 'weight': # decimal
                if question.field_id.minvalue != None:
                    dynamic_args['min_value']=int(question.field_id.minvalue)
                if question.field_id.maxvalue != None:
                    dynamic_args['max_value']=int(question.field_id.maxvalue)
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=int(question.field_id.default_value)
                self.fields['question_' + str(question.id) + '_' + self.event_id] = forms.FloatField( **dynamic_args )
                
            elif question.field_id.datatype == 'boolean':
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=bool(question.field_id.default_value)
                dynamic_args['required'] = False
                self.fields['question_' + str(question.id) + '_' + self.event_id] = forms.BooleanField( **dynamic_args )
                
            elif question.field_id.datatype == 'date':
                if answer.count() == 1:
                    dynamic_args['initial']=datetime.datetime.strptime(answer[0].field_value, "%Y-%m-%d %H:%M:%S.%f")
                elif question.field_id.default_value  != '':
                    dynamic_args['initial']=datetime.datetime.strptime(question.field_id.default_value, "%Y-%m-%d %H:%M:%S.%f")
                else:
                    dynamic_args['initial']=datetime.datetime.now()
                self.fields['question_' + str(question.id) + '_' + self.event_id] = forms.DateField( **dynamic_args )
                
                # elif question.field_id.datatype == 'location':
            
            elif question.field_id.datatype == 'yes_no':
                options = (('yes', 'Yes'), ('no', 'No'))
                dynamic_args['choices'] = options
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=question.field_id.default_value
                self.fields['question_' + str(question.id) + '_' + self.event_id] = forms.ChoiceField( **dynamic_args )
            
            elif question.field_id.datatype == 'text' or question.field_id.datatype == 'location' or question.field_id.datatype == 'other':
                if answer.count() == 1:
                    dynamic_args['initial']=answer[0].field_value
                elif question.field_id.default_value != '':
                    dynamic_args['initial']=question.field_id.default_value
                self.fields['question_' + str(question.id) + '_' + self.event_id] = forms.CharField( **dynamic_args )
            
            self.fields['question_' + str(question.id) + '_' + self.event_id].question = question
            self.fields['question_' + str(question.id) + '_' + self.event_id].answer = answer
            self.fields['question_' + str(question.id) + '_' + self.event_id].event = event
            
    # def save(self, user):
    def save(self):
        for field_name in self.fields:
            field = self.fields[field_name]
            answer = self.cleaned_data[field_name]
            value = FieldValue.objects.get_or_create(event_id=field.event, field_id=field.question.field_id)[0]
            value.field_value=str(answer)
            value.last_modified = datetime.datetime.today()
            value.save()
        return True
           