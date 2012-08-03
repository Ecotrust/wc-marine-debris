from marine_debris.datasheets.models import DataSheet, Field, DataSheetField
from django.contrib import admin
from django.contrib import databrowse
from django.forms import TextInput, Textarea
from django.db import models

databrowse.site.register(Field)
databrowse.site.register(DataSheet)
databrowse.site.register(DataSheetField)

class DataSheetFieldInline(admin.StackedInline):
    model = DataSheet.field.through
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class DataSheetAdmin(admin.ModelAdmin):
    # list_display = ('__unicode__', 'sheetname','media_id','year_started','created_by')
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    inlines = [
        DataSheetFieldInline,
    ]

class FieldAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class DataSheetFieldAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
admin.site.register(Field,FieldAdmin)
admin.site.register(DataSheet,DataSheetAdmin)
admin.site.register(DataSheetField,DataSheetFieldAdmin)
