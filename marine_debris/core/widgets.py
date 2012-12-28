import settings
from django import forms
from django.forms.widgets import *
from django.utils.safestring import mark_safe

class SelectWithTooltip(forms.Select):
    def __init__(self, queryset=None, attrs=None):
        super(SelectWithTooltip, self).__init__(attrs)
        self.attrs = attrs

    def render(self, *args, **kwargs): 
        output = super(SelectWithTooltip, self).render(*args,**kwargs) 
        output = output + '<img src="%simg/info.png" id="info_%s" class="field-tooltip" title="%s" rel="%s" data-placement="%s" />' % (settings.STATIC_URL, self.attrs['tool-id'], self.attrs['tool-title'], self.attrs['tool-rel'], self.attrs['tool-data-placement'])
        # print output
        return mark_safe(output)  
        
class TextInputWithTooltip(forms.TextInput):
    def __init__(self, queryset=None, attrs=None):
        super(TextInputWithTooltip, self).__init__(attrs)
        self.attrs = attrs

    def render(self, *args, **kwargs): 
        output = super(TextInputWithTooltip, self).render(*args,**kwargs) 
        output = output + '<img src="%simg/info.png" id="info_%s" class="field-tooltip" title="%s" rel="%s" data-placement="%s" />' % (settings.STATIC_URL, self.attrs['tool-id'], self.attrs['tool-title'], self.attrs['tool-rel'], self.attrs['tool-data-placement'])
        #print output
        return mark_safe(output)
        
class FileFieldWithTooltip(forms.ClearableFileInput):
    def __init__(self, attrs=None):
        super(FileFieldWithTooltip, self).__init__(attrs)
        self.attrs = attrs

    def render(self, *args, **kwargs): 
        output = super(FileFieldWithTooltip, self).render(*args,**kwargs) 
        output = output + '<img src="%simg/info.png" id="info_%s" class="field-tooltip" title="%s" rel="%s" data-placement="%s" />' % (settings.STATIC_URL, self.attrs['tool-id'], self.attrs['tool-title'], self.attrs['tool-rel'], self.attrs['tool-data-placement'])
        #print output
        return mark_safe(output)