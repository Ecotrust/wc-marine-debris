from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

# Create your models here.
class DataType (models.Model):
    name = models.TextField()
    
    def __unicode__(self):
        return self.name

class Unit (models.Model):
    short_name = models.TextField()
    long_name = models.TextField()
    data_type = models.ForeignKey(DataType, null=True, blank=True)
    
    def __unicode__(self):
        return self.long_name
        
    class Meta:
        ordering = ['long_name']
        
class Organization (models.Model):
    orgname = models.TextField()
    contact = models.TextField()
    phone = models.TextField()
    address = models.TextField()
    
    def __unicode__(self):
        return self.orgname
        
    class Meta:
        ordering = ['orgname']

class Grouping (models.Model):
    name = models.TextField()
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        ordering = ['name']
        
class AnswerOption(models.Model):
    eng_text = models.TextField()
    display_order = models.FloatField()
    
    class Meta:
        ordering = ['display_order']
        
    def __unicode__(self):
        return self.eng_text
        
class Field (models.Model):
    unit_id = models.ForeignKey(Unit, blank=True, null=True) 
    internal_name = models.TextField()
    datatype = models.ForeignKey(DataType, default=8)
    minvalue = models.IntegerField(blank=True, null=True)
    maxvalue = models.IntegerField(blank=True, null=True)
    default_value = models.TextField(blank=True, null=True)  #TODO: What type should this be? Should it be part of Unit? FieldValue?
    required = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.internal_name
        
    class Meta:
        ordering = ['internal_name']
    
class EventType (models.Model):
    type = models.TextField()
    display_sites = models.BooleanField(default=True, help_text="Use \'Display Sites\' to determine if site-names will be used - primarily for beach cleanups, and not for derelict gear")
    
    def __unicode__(self):
        return self.type
        
    class Meta:
        ordering = ['type']
    
class DataSheet (models.Model):
    sheetname = models.TextField()
    created_by = models.ForeignKey(Organization)
    year_started = models.IntegerField()
    # media_id = models.ForeignKey(Media, blank=True, null=True)
    field = models.ManyToManyField(Field, through='DataSheetField')
    type_id = models.ForeignKey(EventType, null=True, blank=True)
    
    def __unicode__(self):
        return self.sheetname
        
    class Meta:
        ordering = ['sheetname']
    
class DataSheetField (models.Model):
    field_id = models.ForeignKey(Field)
    sheet_id = models.ForeignKey(DataSheet)
    field_name = models.TextField()
    print_name = models.TextField(blank=True, null=True)
    unit_id = models.ForeignKey(Unit, blank=True, null=True)
    grouping = models.ForeignKey(Grouping, null=True, blank=True)   #TODO: Name 'category' already claimed. Maybe 'group' or 'subgroup'?
    answer_options = models.ManyToManyField(AnswerOption, help_text='if a list question, multi-select valid responses', blank=True, null=True)
    required = models.BooleanField(default=False)
    
    def __unicode__(self):
        readable_name = self.field_name + '-' + self.sheet_id.sheetname + '-' + self.field_id.internal_name
        return readable_name
        
    class Meta:
        ordering = ['field_name', 'sheet_id__sheetname', 'field_id__internal_name']
    
class Project (models.Model):
    projname = models.TextField()
    organization = models.ManyToManyField(Organization, through='ProjectOrganization')
    website = models.TextField(blank=True, null=True)
    contact_name = models.TextField(blank=True, null=True)
    contact_email = models.TextField(blank=True, null=True)
    contact_phone = models.TextField(blank=True, null=True)
    active_sheets = models.ManyToManyField(DataSheet, through='ProjectDataSheet')
    
    def __unicode__(self):
        return self.projname
        
    class Meta:
        ordering = ['projname']
    
class ProjectOrganization (models.Model):
    organization_id = models.ForeignKey(Organization)
    project_id = models.ForeignKey(Project)
    is_lead = models.BooleanField(default=False)
    
    def __unicode__(self):
        readable_name = self.organization_id.orgname + '-' + self.project_id.projname
        return readable_name
        
    class Meta:
        ordering = ['organization_id__orgname', 'project_id__projname']

class Media (models.Model):
    type = models.TextField()
    filename = models.TextField()
    proj_id = models.ForeignKey(Project)
    published = models.DateTimeField( blank=True, null=True, default=datetime.datetime.now)
    
    def __unicode__(self):
        return self.proj_id.projname + '-' + self.filename
        
    class Meta:
        ordering = ['proj_id__projname', 'filename']
    
class ProjectDataSheet (models.Model):
    project_id = models.ForeignKey(Project)
    sheet_id = models.ForeignKey(DataSheet)
    
    def __unicode__(self):
        readable_name = self.project_id.projname + '-' + self.sheet_id.sheetname
        return readable_name
        
    class Meta:
        ordering = ['project_id__projname', 'sheet_id__sheetname']
        
class State (models.Model):
    name = models.TextField()
    initials = models.TextField()
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        ordering = ['name', 'initials']
        
class Event (models.Model):
    datasheet_id = models.ForeignKey(DataSheet)
    proj_id = models.ForeignKey(Project)
    cleanupdate = models.DateTimeField(default=datetime.date.today)
    sitename = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True, validators=[MinValueValidator(32.5), MaxValueValidator(49.1)])
    lon = models.FloatField(blank=True, null=True, validators=[MinValueValidator(-124.8), MaxValueValidator(-117)])
    city = models.TextField(blank=True, null=True)
    state = models.ForeignKey(State, default=1)
    county = models.TextField(blank=True, null=True)
    # type_id = models.ForeignKey(EventType, null=True, blank=True)
    
    def __unicode__(self):
        return self.proj_id.projname + '-' + self.sitename + '-' + self.cleanupdate.date().isoformat()
        
    def get_fields(self):
        return[(field.name, field.value_to_string(self)) for field in Event._meta.fields]
        
    class Meta:
        ordering = ['proj_id__projname', 'sitename', 'cleanupdate']
    
class FieldValue (models.Model):
    field_id = models.ForeignKey(Field)
    event_id = models.ForeignKey(Event)
    field_value = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        readable_name = str(self.event_id) + '-' + self.field_id.internal_name
        return readable_name
        
    class Meta:
        ordering = ['event_id', 'field_id__internal_name']
    