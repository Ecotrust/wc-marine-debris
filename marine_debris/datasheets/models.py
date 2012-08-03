from django.db import models
import datetime

# Create your models here.
class Unit (models.Model):
    short_name = models.TextField()
    long_name = models.TextField()
    
    def __unicode__(self):
        return self.long_name
    
class Organization (models.Model):
    orgname = models.TextField()
    contact = models.TextField()
    phone = models.TextField()
    address = models.TextField()
    
    def __unicode__(self):
        return self.orgname
    
class Media (models.Model):
    type = models.TextField()
    filename = models.TextField()
    org_id = models.ForeignKey(Organization)
    published = models.DateTimeField( blank=True, null=True, default=datetime.datetime.now)
    
    def __unicode__(self):
        return self.org_id.orgname + '-' + self.filename
        
class Category (models.Model):
    name = models.TextField()
    
    def __unicode__(self):
        return self.name

class Field (models.Model):
    dataTypeChoices = (
        ('text', 'Text'),
        ('number', 'Number'),
        ('weight', 'Weight'),
        ('distance', 'Distance'),
        ('area', 'Area'),
        ('volume', 'Volume'),
        ('date', 'Date'),
        ('duration', 'Duration'),
        ('boolean', 'True/False'),
        ('yes_no', 'Yes/No'),
        ('other', 'Other')
    )
    unit_id = models.ForeignKey(Unit) 
    internal_name = models.TextField()
    datatype = models.CharField(max_length=255, choices=dataTypeChoices)
    minvalue = models.IntegerField(blank=True, null=True)
    maxvalue = models.IntegerField(blank=True, null=True)
    default_value = models.TextField(blank=True, null=True)  #TODO: What type should this be? Should it be part of Unit? FieldValue?
    
    def __unicode__(self):
        return self.internal_name
    
class DataSheet (models.Model):
    sheetname = models.TextField()
    created_by = models.ForeignKey(Organization)
    year_started = models.IntegerField()
    media_id = models.ForeignKey(Media, blank=True, null=True)
    field = models.ManyToManyField(Field, through='DataSheetField')
    
    def __unicode__(self):
        return self.sheetname
    
class DataSheetField (models.Model):
    field_id = models.ForeignKey(Field)
    sheet_id = models.ForeignKey(DataSheet)
    print_name = models.TextField()
    field_name = models.TextField()
    unit_id = models.ForeignKey(Unit)
    category = models.ForeignKey(Category, null=True, blank=True)
    
    def __unicode__(self):
        readable_name = self.field_name + '-' + self.sheet_id.sheetname + '-' + self.field_id.internal_name
        return readable_name
    