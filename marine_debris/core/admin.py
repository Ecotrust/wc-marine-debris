from core.models import *
from django.contrib import admin
from django.contrib import databrowse
from django.forms import TextInput, Textarea
from django.db import models


databrowse.site.register(AnswerOption)
databrowse.site.register(County)
databrowse.site.register(DataSheet)
databrowse.site.register(DataSheetField)
databrowse.site.register(DataType)
databrowse.site.register(Event)
databrowse.site.register(EventType)
databrowse.site.register(Field)
databrowse.site.register(FieldValue)
databrowse.site.register(Grouping)
databrowse.site.register(Media)
databrowse.site.register(Organization)
databrowse.site.register(Project)
databrowse.site.register(ProjectOrganization)
databrowse.site.register(Site)
databrowse.site.register(State)
databrowse.site.register(Unit)
databrowse.site.register(UnitConversion)
databrowse.site.register(Download)
databrowse.site.register(UserTransaction)
  
class DataSheetFieldInline(admin.TabularInline):
    model = DataSheetField
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class ProjectDataSheetInline(admin.TabularInline):
    model = Project.active_sheets.through
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
      
class ProjectOrganizationInline(admin.TabularInline):
    model = Project.organization.through
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
     
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ('eng_text', 'display_order')
    search_fields = ['eng_text']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'stateabr')
    search_fields = ('name', 'stateabr')
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class DataSheetAdmin(admin.ModelAdmin):
    list_display = ('slug', '__unicode__', 'type_id', 'created_by', 'year_started')
    search_fields = ('slug', 'sheetname', 'type_id__type', 'created_by__orgname', 'year_started')
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    inlines = [
        DataSheetFieldInline,
    ]
    
class DataSheetFieldAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'field_name', 'sheet_id', 'field_id', 'print_name', 'grouping', 'unit_id')
    search_fields = ['field_name', 'sheet_id__sheetname', 'field_id__internal_name', 'sheet_id__id', 'field_id__id', 'print_name', 'grouping__name', 'unit_id__long_name']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }

class DataTypeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'name', 'aggregatable')
    search_fields = ['name', 'aggregatable']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
  
class EventAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'proj_id', 'cleanupdate', 'datasheet_id', 'site')
    search_fields = ['proj_id__projname', 'site__sitename', 'cleanupdate', 'datasheet_id__sheetname', 'site__sitename']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
   
class EventTypeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
   
class FieldAdmin(admin.ModelAdmin):
    list_display = ('label', '__unicode__', 'description', 'datatype', 'unit_id', 'minvalue', 'maxvalue', 'default_value')
    search_fields = ['label', 'internal_name', 'description', 'datatype__name', 'unit_id__long_name']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class FieldValueAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'field_value', 'event_id', 'field_id')
    search_fields = ['field_value', 'event_id__proj_id__projname', 'event_id__site__sitename', 'field_id__internal_name', 'field_id__label']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
      
class GroupingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
 
class MediaAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'filename', 'type', 'proj_id', 'published')
    search_fields = ['filename', 'type', 'proj_id__projname', 'published']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
 
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'orgname', 'address', 'city', 'state', 'zip', 'scope', 'url')
    search_fields = ['orgname', 'address', 'city', 'state', 'zip', 'scope', 'url']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('projname', 'website', 'contact_name', 'contact_title', 'contact_email', 'contact_phone')
    search_fields = ['projname', 'website', 'contact_name', 'contact_title', 'contact_email', 'contact_phone']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    inlines = [
        ProjectOrganizationInline,
        ProjectDataSheetInline,
    ]
  
class ProjectOrganizationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'organization_id', 'project_id', 'is_lead')
    search_fields = ['organization_id__orgname', 'project_id__projname', 'is_lead']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
 
class SiteAdmin(admin.ModelAdmin):
    list_display = ('sitename', 'state', 'county', 'geometry')
    search_fields = ['sitename', 'state__name', 'county']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
   
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'initials')
    search_fields = ['name', 'initials']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
   
class UnitAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'short_name', 'data_type')
    search_fields = ['long_name', 'short_name', 'data_type__name']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
      
class UnitConversionAdmin(admin.ModelAdmin):
    list_display = ('from_unit', 'to_unit', 'factor')
    search_fields = ['from_unit__long_name', 'to_unit__long_name', 'factor']

class DownloadAdmin(admin.ModelAdmin):
    list_display = ('label', 'description', 'file_prefix', 'category', 'pretty_print', 'auto_generate', 'filter_string')
    search_fields = ['label', 'description', 'file_prefix', 'category', 'pretty_print', 'auto_generate', 'filter_string']

class UserTransactionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'submitted_by', 'organization', 'project', 'created_date', 'status', 'reason')
    search_fields = ['submitted_by__username', 'organization__orgname', 'project__projname', 'created_date', 'status', 'reason']
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
    
admin.site.register(AnswerOption,AnswerOptionAdmin)
admin.site.register(County,CountyAdmin)
admin.site.register(DataSheet,DataSheetAdmin)
admin.site.register(DataSheetField,DataSheetFieldAdmin)
admin.site.register(DataType,DataTypeAdmin)
admin.site.register(Event,EventAdmin)
admin.site.register(EventType,EventTypeAdmin)
admin.site.register(Field,FieldAdmin)
admin.site.register(FieldValue,FieldValueAdmin)
admin.site.register(Grouping,GroupingAdmin)
admin.site.register(Media,MediaAdmin)
admin.site.register(Organization,OrganizationAdmin)
admin.site.register(Project,ProjectAdmin)
admin.site.register(ProjectOrganization,ProjectOrganizationAdmin)
admin.site.register(Site,SiteAdmin)
admin.site.register(State,StateAdmin)
admin.site.register(Unit,UnitAdmin)
admin.site.register(UnitConversion,UnitConversionAdmin)
admin.site.register(Download,DownloadAdmin)
admin.site.register(UserTransaction,UserTransactionAdmin)
