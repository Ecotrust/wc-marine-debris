import settings
from django import forms
from django.forms.widgets import *
from django.utils.safestring import mark_safe

class SelectWithTooltip(forms.Select):
    def __init__(self, queryset=None, attrs=None):
        super(SelectWithTooltip, self).__init__(attrs)
        self.attrs = attrs

    def render(self, *args, **kwargs): 
    
        if settings.SERVER == 'Dev':
            static_media_url = settings.MEDIA_URL
        else:
            static_media_url = settings.STATIC_URL
    
        output = super(SelectWithTooltip, self).render(*args,**kwargs) 
        output = output + '<img src="%simg/info.png" id="info_%s" class="tooltip" />' % (settings.STATIC_URL, self.attrs['tool-id'])
        #print output
        return mark_safe(output)  
        
class TextInputWithTooltip(forms.TextInput):
    def __init__(self, queryset=None, attrs=None):
        super(TextInputWithTooltip, self).__init__(attrs)
        self.attrs = attrs

    def render(self, *args, **kwargs): 
    
        if settings.SERVER == 'Dev':
            static_media_url = settings.MEDIA_URL
        else:
            static_media_url = settings.STATIC_URL
    
        output = super(TextInputWithTooltip, self).render(*args,**kwargs) 
        output = output + '<img src="%simg/info.png" id="info_%s" class="tooltip" />' % (settings.STATIC_URL, self.attrs['tool-id'])
        #print output
        return mark_safe(output)