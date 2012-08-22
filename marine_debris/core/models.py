from django.db import models
import datetime

# Create your models here.
class Unit (models.Model):
    short_name = models.TextField()
    long_name = models.TextField()
    
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
    
class Project (models.Model):
    projname = models.TextField()
    organizations = models.ManyToManyField(Organization, through='ProjectOrganization')
    website = models.TextField(blank=True, null=True)
    contact_name = models.TextField(blank=True, null=True)
    contact_email = models.TextField(blank=True, null=True)
    contact_phone = models.TextField(blank=True, null=True)
    
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
        ordering = ['oragnization_id__orgname', 'project_id__projname']

class Media (models.Model):
    type = models.TextField()
    filename = models.TextField()
    proj_id = models.ForeignKey(Project)
    published = models.DateTimeField( blank=True, null=True, default=datetime.datetime.now)
    
    def __unicode__(self):
        return self.proj_id.projname + '-' + self.filename
        
    class Meta:
        ordering = ['proj_id__projname', 'filename']
    
class Category (models.Model):
    name = models.TextField()
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        ordering = ['name']

class Field (models.Model):
    dataTypeChoices = (
        ('area', 'Area'),
        ('boolean', 'True/False'),
        ('date', 'Date'),
        ('distance', 'Distance'),
        ('duration', 'Duration'),
        ('location', 'Location'),
        ('number', 'Number'),
        ('text', 'Text'),
        ('volume', 'Volume'),
        ('weight', 'Weight'),
        ('yes_no', 'Yes/No'),
        ('other', 'Other')
    )
    unit_id = models.ForeignKey(Unit, blank=True, null=True) 
    internal_name = models.TextField()
    datatype = models.CharField(max_length=255, choices=dataTypeChoices)
    minvalue = models.IntegerField(blank=True, null=True)
    maxvalue = models.IntegerField(blank=True, null=True)
    default_value = models.TextField(blank=True, null=True)  #TODO: What type should this be? Should it be part of Unit? FieldValue?
    
    def __unicode__(self):
        return self.internal_name
        
    class Meta:
        ordering = ['internal_name']
    
class DataSheet (models.Model):
    sheetname = models.TextField()
    created_by = models.ForeignKey(Organization)
    year_started = models.IntegerField()
    media_id = models.ForeignKey(Media, blank=True, null=True)
    field = models.ManyToManyField(Field, through='DataSheetField')
    
    def __unicode__(self):
        return self.sheetname
        
    class Meta:
        ordering = ['sheetname']
    
class DataSheetField (models.Model):
    field_id = models.ForeignKey(Field)
    sheet_id = models.ForeignKey(DataSheet)
    print_name = models.TextField(blank=True, null=True)
    field_name = models.TextField()
    unit_id = models.ForeignKey(Unit, blank=True, null=True)
    category = models.ForeignKey(Category, null=True, blank=True)
    
    def __unicode__(self):
        readable_name = self.field_name + '-' + self.sheet_id.sheetname + '-' + self.field_id.internal_name
        return readable_name
        
    class Meta:
        ordering = ['field_name', 'sheet_id__sheetname', 'field_id__internal_name']
    
class EventType (models.Model):
    type = models.TextField()
    
    def __unicode__(self):
        return self.type
        
    class Meta:
        ordering = ['type']
    
class Event (models.Model):
    datasheet_id = models.ForeignKey(DataSheet)
    proj_id = models.ForeignKey(Project)
    type_id = models.ForeignKey(EventType)
    cleanupdate = models.DateTimeField(default=datetime.datetime.now)
    sitename = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    county = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.proj_id.projname + '-' + self.sitename + '-' + self.cleanupdate.date().isoformat()
        
    class Meta:
        ordering = ['proj_id__projname', 'sitename', 'cleanupdate']
    