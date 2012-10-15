#from django.db import models
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.conf import settings
import datetime
from datetime import date
from django.contrib.gis.admin import OSMGeoAdmin
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^django\.contrib\.gis\.db\.models\.fields\.PointField"])
from django.core.cache import cache

# Create your models here.
class DataType (models.Model):
    name = models.TextField()
    aggregatable = models.BooleanField(default=False)
    
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
    users = models.ManyToManyField(User)
    
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
    def internal_fieldname_lookup(self):
        """
        returns 
        {
            'Internal_Name': 'Datasheet Field Name',
            .....
        }
        """
        return dict([(x.field_id.internal_name, x.field_name) for x in self.datasheetfield_set.all()])

    @property
    def unit_lookup(self):
        """
        returns
        {
            'Internal_Name': 'Datasheet Field Unit',
            .....
        }
        """
        return dict([(datasheet.field_id.internal_name, datasheet.unit_id.short_name) for datasheet in self.datasheetfield_set.all() if datasheet.unit_id])
        
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
        if self.type_id:
            type = self.type_id.type
        else:
            type = 'None'
        ds_dict = {
            'name': self.sheetname,
            'start_date': self.year_started,
            'id': self.id,
            'event_type':type,
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
        unique_together = (("name", "initials"))
        
    @property
    def toDict(self):
        timeout=60*60*24*7
        key = 'statecache_%s' % self.id
        res = cache.get(key)
        if res == None:
            counties = [x.county for x in Site.objects.filter(state=self).distinct('county')]
            counties_list = []
            for county in counties:
                sites = [x.toDict for x in Site.objects.filter(state=self, county=county)]
                county_dict = { 'name': county, 'sites': sites }
                counties_list.append(county_dict)
            res = {
                'name': self.name,
                'initials': self.initials,
                'counties': counties_list
            }
            cache.set(key, res, timeout)
        return res
        
    @property
    def toSimpleDict(self):
        return {
            'name': self.name,
            'initials': self.initials,
            'type': 'state',
        }
        
class Site (models.Model):
    sitename = models.TextField(blank=True, null=True)
    state = models.ForeignKey(State, blank=True, null=True)
    county = models.TextField(blank=True, null=True)
    geometry = models.PointField(srid=settings.SERVER_SRID, null=True, blank=True)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return unicode(self.sitename)
        
    @property
    def countyDict(self):
        sites = [ site.toDict for site in Site.objects.filter(county = self.county)]
        if self.county:
            county = self.county
        else:
            county = ''
        county_dict = {
            'name': county,
            'sites': sites
        }
        return county_dict
        
    @property
    def toDict(self):
        if self.geometry:
            lat = self.geometry.get_coords()[1]
            lon = self.geometry.get_coords()[0]
        else:
            lat = '' 
            lon = ''
        if self.sitename:
            sitename = self.sitename
        else:
            sitename = ''
        if self.state:
            state = self.state.name
            st_initials = self.state.initials
        else:
            state = ''
            st_initials = ''
        if self.county:
            county = self.county
        else:
            county = ''
        site_dict = {
            'name': sitename,
            'lat': lat,
            'lon': lon,
            'state': state,
            'st_initials': st_initials,
            'county': county
        }
        return site_dict
        
    class Meta:
        unique_together = (("sitename", "state", "county"))
        
    def impute_state_county(self):
        '''
        Based on the geometry, sets state and county
        '''
        pnt = self.geometry
        counties = County.objects.filter(geom__bboverlaps=pnt.buffer(1)) # search in a 1 degree radius

        closest = None
        shortest_distance = 181
        for county in counties:
            if county.geom.intersects(pnt):
                # direct hit
                closest = county
                break
            d = county.geom.distance(pnt)
            if d < shortest_distance:
                # look for the closest if no direct hit
                closest = county
                shortest_distance = d

        if not closest:
            return None

        self.county = closest.name
        self.state = State.objects.filter(initials=closest.stateabr)[0]

        return closest

    def save(self, *args, **kwargs):
        if not self.sitename or self.sitename.strip() == '':
            self.sitename = str(self.geometry.get_coords()[0]) + ', ' + str(self.geometry.get_coords()[1])

        if (not self.state or not self.county) and self.geometry:
            self.impute_state_county()
        
        if self.state:
            key = 'statecache_%s' % self.state.id
            cache.delete(key)
        
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
    dup = models.IntegerField(default=0)
    submitted_by = models.ForeignKey(User, null=True, blank=True, default=None)
    status = models.CharField(max_length=30, choices=StatusChoices, default='New', blank=True)
    
    def __unicode__(self):
        return "%s-%s-%s" % (self.proj_id.projname, self.site.sitename, self.cleanupdate.isoformat())
        
    def get_fields(self):
        return[(field.name, field.value_to_string(self)) for field in Event._meta.fields]
        
    @property
    def field_values(self):
        """
        return dict with keys as datasheet field names and values
        """
        fvals = FieldValue.objects.filter(event_id=self)
        lut = self.datasheet_id.internal_fieldname_lookup
        rvals = {}
        for fval in fvals:
            key = unicode(lut[fval.field_id.internal_name])
            rvals[key] = (fval.field_value, fval.field_id.datatype.name)
        return rvals
        
    @property
    def field_values_list(self):
        """
        return a list of dicts of field values. KEYS: 'text', 'value', 'unit'
        """
        fvals = FieldValue.objects.filter(event_id=self)
        name_lut = self.datasheet_id.internal_fieldname_lookup
        unit_lut = self.datasheet_id.unit_lookup
        rvals = []
        for fval in fvals:
            text = unicode(name_lut[fval.field_id.internal_name])
            value = fval.field_value
            if fval.field_id.internal_name in unit_lut.keys():
                unit = unicode(unit_lut[fval.field_id.internal_name])
            else:
                unit = ''
            if value.isalpha() and value == 'None' or value == '':
                value = ''
                unit = ''
            else:
                try:
                    if float(value) == 0.0:
                        value = ''
                        unit = ''
                except ValueError:
                    pass
            if unit == 'Text' or unit == 'Count':
                unit = ''
            rvals.append({
                'text': text,
                'value': value, 
                'unit': unit
            })
        return rvals

    @property
    def toDict(self):
        return {
            "site": self.site.toDict,
            "project": self.proj_id.toDict,
            "id": self.id,
            "datasheet": self.datasheet_id.toDict
        } 
        
    @property
    def toEventsDict(self):
        proj = self.proj_id
        return {
            "site": self.site.toDict,
            "project": {
                "name": proj.projname
            },
            "id": self.id,
            "datasheet": self.datasheet_id.toDict,
            "organization": {
                "name": proj.projectorganization_set.order_by('-is_lead')[0].organization_id.orgname
            },
            "date" : self.cleanupdate.strftime('%m/%d/%Y')
        } 
        
    def save(self, *args, **kwargs):
        
        if self.id:
            key = 'eventcache_%s' % self.id
            cache.delete(key)
        
        super(Event, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['proj_id__projname', 'site', 'cleanupdate']
        unique_together = (("datasheet_id", "proj_id", "cleanupdate", "site", "dup"),)
    
class FieldValue (models.Model):
    field_id = models.ForeignKey(Field)
    event_id = models.ForeignKey(Event)
    field_value = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        readable_name = str(self.event_id) + '-' + self.field_id.internal_name
        return readable_name
        
    class Meta:
        ordering = ['event_id', 'field_id__internal_name']
    

# This is an auto-generated Django model module created by ogrinspect.
class County(models.Model):
    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    name = models.CharField(max_length=100)
    stateabr = models.CharField(max_length=2)
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

# Auto-generated `LayerMapping` dictionary for County model
county_mapping = {
    'statefp' : 'STATEFP',
    'countyfp' : 'COUNTYFP',
    'name' : 'NAME',
    'stateabr' : 'STATEABR',
    'geom' : 'MULTIPOLYGON',
}


from django.contrib.gis.utils import LayerMapping
def load_shp(path, feature_class):
    '''
    Loads a shapefile into a model (used to load Counties in this case)
    First we ran ogrinspect to generate the class and mapping. 
        python manage.py ogrinspect ~/projects/marine_debris/counties/western_counties.shp County --mapping --srid=4326 --multi
    Pasted code into models.py and modified as necessary.
    Finally, loaded the shapefile from shell:
        from core import models
        models.load_shp('/home/mperry/projects/marine_debris/counties/western_counties.shp', models.County)
    '''
    mapping = eval("%s_mapping" % feature_class.__name__.lower())
    print "Saving", path, "to", feature_class, "using", mapping
    map1 = LayerMapping(feature_class, path, mapping, transform=False, encoding='iso-8859-1')
    map1.save(strict=True, verbose=True)
