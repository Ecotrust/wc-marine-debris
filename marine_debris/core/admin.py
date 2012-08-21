from core.models import DataSheet, Field, DataSheetField, Unit, Organization, Media, Category
from django.contrib import admin
from django.contrib import databrowse
from django.forms import TextInput, Textarea
from django.db import models

databrowse.site.register(Field)
databrowse.site.register(DataSheet)
databrowse.site.register(DataSheetField)
databrowse.site.register(Unit)
databrowse.site.register(Organization)
databrowse.site.register(Media)
databrowse.site.register(Category)

class UnitAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class OrganizationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class MediaAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class CategoryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class DataSheetFieldInline(admin.TabularInline):
    model = DataSheet.field.through
    formfield_overrides = {
        models.TextField: {
            'widget': TextInput()
        },
    }
    
class DataSheetAdmin(admin.ModelAdmin):
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
    
admin.site.register(Unit,UnitAdmin)
admin.site.register(Organization,OrganizationAdmin)
admin.site.register(Media,MediaAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Field,FieldAdmin)
admin.site.register(DataSheet,DataSheetAdmin)
admin.site.register(DataSheetField,DataSheetFieldAdmin)
