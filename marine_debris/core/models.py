from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.conf import settings
import datetime
from datetime import date

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
        
    @property
    def toDict(self):
        projects = [project.toDict for project in Project.objects.filter(organization = self)]
        org_dict = {
            'name': self.orgname,
            'projects': projects,
        }
        return org_dict

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
    

class DataSheetError(Exception):
    pass

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
        
    @property
    def fieldnames(self):
        return [f.field_name for f in self.datasheetfield_set.all()]

    @property
    def required_fieldnames(self):
        """
        Collects the fieldnames for required fields of two types:
         - globally required in settings
         - required per datasheet
        """
        # global
        req_fields = settings.REQUIRED_FIELDS[self.site_type] 
        required_fieldnames = []
        for item, internal_name in req_fields.items():
            try:
                dsf = self.datasheetfield_set.get(field_id__internal_name=internal_name)
            except DataSheetField.DoesNotExist:
                raise DataSheetError("DataSheet (id=%d) should have a field with internal_name of '%s'" % (self.pk, internal_name,))
            required_fieldnames.append(dsf.field_name)

        # per datasheet
        ds_req_fields = self.datasheetfield_set.filter(required=True)
        for rf in ds_req_fields:
            fieldname = rf.field_name
            if fieldname not in required_fieldnames:
                required_fieldnames.append(fieldname)

        return required_fieldnames

    @property
    def site_type(self):
        if self.site_based:
            return "site-based"
        else:
            return "coord-based"

    @property
    def site_based(self):
        if self.type_id:
            use_sites = self.type_id.display_sites
        else:
            use_sites = True #default
        return use_sites

    def is_valid(self):
        try: 
            self.required_fieldnames
        except DataSheetError as e:
            return (False, e.message)
        # test for type_id?
        return (True, "Valid")

    @property
    def toDict(self):
        ds_dict = {
            'name': self.sheetname,
            'start_date': self.year_started,
            'id': self.id,
        }
        return ds_dict
    
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
        return "%s-%s-%s" % (self.field_name, self.sheet_id.sheetname, self.field_id.internal_name)
        
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
        
    @property
    def toDict(self):
        datasheets = [datasheet.toDict for datasheet in self.active_sheets.all()]
        proj_dict = {
            'name': self.projname,
            'datasheets': datasheets,
        }
        return proj_dict
    
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
    
    def __repr__(self):
        return self.name

    def __unicode__(self):
        return self.name
        
    class Meta:
        ordering = ['name', 'initials']
        
    @property
    def toDict(self):
        counties = [ site.countyDict for site in Site.objects.filter(state=self)]
        state_dict = {
            'name': self.name,
            'initials': self.initials,
            'counties': counties
        }
        return state_dict
        
class Site (models.Model):
    sitename = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True, validators=[MinValueValidator(32.5), MaxValueValidator(49.1)])
    lon = models.FloatField(blank=True, null=True, validators=[MinValueValidator(-124.8), MaxValueValidator(-117)])
    state = models.ForeignKey(State, blank=True, null=True)
    county = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return unicode(self.sitename)
        
    @property
    def countyDict(self):
        sites = [ site.toDict for site in Site.objects.filter(county = self.county)]
        county_dict = {
            'name': self.county,
            'sites': sites
        }
        return county_dict
        
    @property
    def toDict(self):
        site_dict = {
            'name': self.sitename,
            'lat': self.lat,
            'lon': self.lon,
            'state': self.state.name,
            'county': self.county
        }
        return site_dict
        
    class Meta:
        unique_together = (("sitename", "state", "county"), ("lat", "lon"))
        
    def save(self, *args, **kwargs):
        if not self.sitename or self.sitename.strip() == '':
            self.sitename = str(self.lon) + ', ' + str(self.lat)
        #TODO if not state or county, determine based on coords?
        super(Site, self).save(*args, **kwargs)

class Event (models.Model):
    
    StatusChoices = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected')
    )
    datasheet_id = models.ForeignKey(DataSheet)
    proj_id = models.ForeignKey(Project)
    cleanupdate = models.DateField(default=datetime.date.today())
    site = models.ForeignKey(Site, null=True, blank=True, default= None)
    submitted_by = models.ForeignKey(User, null=True, blank=True, default=None)
    status = models.CharField(max_length=30, choices=StatusChoices, default='New', blank=True)
    
    def __unicode__(self):
        return "%s-%s-%s" % (self.proj_id.projname, self.site.sitename, self.cleanupdate.isoformat())
        
    def get_fields(self):
        return[(field.name, field.value_to_string(self)) for field in Event._meta.fields]
        
    class Meta:
        ordering = ['proj_id__projname', 'site', 'cleanupdate']
        unique_together = (("datasheet_id", "proj_id", "cleanupdate", "site"),)
    
class FieldValue (models.Model):
    field_id = models.ForeignKey(Field)
    event_id = models.ForeignKey(Event)
    field_value = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        readable_name = str(self.event_id) + '-' + self.field_id.internal_name
        return readable_name
        
    class Meta:
        ordering = ['event_id', 'field_id__internal_name']
    
