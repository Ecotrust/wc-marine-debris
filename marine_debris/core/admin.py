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
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class CountyAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'name', 'stateabr')
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class DataSheetAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'type_id', 'created_by', 'year_started')
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
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }

class DataTypeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'name', 'aggregatable')
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
  
class EventAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'proj_id', 'cleanupdate', 'datasheet_id', 'site')
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
    list_display = ('__unicode__', 'description', 'datatype', 'unit_id', 'minvalue', 'maxvalue', 'default_value')
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class FieldValueAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'field_value', 'event_id', 'field_id', 'id')
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
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
 
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'orgname', 'address')
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'projname', 'website', 'contact_name', 'contact_email', 'contact_phone')
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
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
 
class SiteAdmin(admin.ModelAdmin):
    list_display = ('sitename', 'state', 'county', 'geometry')
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
   
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'initials')
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
   
class UnitAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'short_name')
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
      
class UserTransactionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'submitted_by', 'organization', 'project', 'created_date', 'status')
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
admin.site.register(UserTransaction,UserTransactionAdmin)
