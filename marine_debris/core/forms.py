from django import forms
from models import *
from django.forms.util import ValidationError
from django.forms.util import ErrorList
import re
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
