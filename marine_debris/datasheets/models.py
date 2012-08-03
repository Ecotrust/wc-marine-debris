from django.db import models

# Create your models here.
class Field (models.Model):
    unit_id = models.IntegerField() #TODO: ForeignKey Unit
    internal_name = models.TextField()
    datatype = models.CharField(max_length=255)   #TODO: What type should this be?
    minvalue = models.IntegerField(blank=True, null=True)
    maxvalue = models.IntegerField(blank=True, null=True)
    default_value = models.CharField(blank=True, null=True, max_length=255)  #TODO: What type should this be? Should it be part of Unit? FieldValue?
    
    def __unicode__(self):
        return self.field_name
    
class DataSheet (models.Model):
    sheetname = models.CharField(max_length=255)
    media_id = models.IntegerField()    #TODO: ForeignKey Media
    year_started = models.IntegerField()
    created_by = models.CharField(max_length=100)   #TODO: ForeignKey Organization
    field = models.ManyToManyField(Field, through='DataSheetField')
    
    def __unicode__(self):
        return self.sheetname
    
class DataSheetField (models.Model):
    field_id = models.ForeignKey(Field)
    sheet_id = models.ForeignKey(DataSheet)
    print_name = models.TextField()
    field_name = models.TextField()
    
    def __unicode__(self):
        readable_name = self.label + '-' + self.sheet_id.sheetname + '-' + self.field_id.field_name
        return readable_name