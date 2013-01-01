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
from django.contrib.gis.geos import Polygon
from django.template.defaultfilters import slugify
from pytz import timezone
import pytz
import urllib
import time

# Create your models here.
class DataType (models.Model):
    name = models.TextField()
    aggregatable = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name


class ConversionError(Exception):
    pass


class Unit(models.Model):
    short_name = models.TextField()
    long_name = models.TextField()
    data_type = models.ForeignKey(DataType, null=True, blank=True)
    slug = models.TextField(unique=True)
    
    def __unicode__(self):
        return self.long_name
        
    @property
    def toDict(self):
        if self.data_type:
            data_type = {
                'name': self.data_type.name,
                'aggregatabale': self.data_type.aggregatable
            }
        else:
            data_type = {
                'name': '',
                'aggregatable': ''
            }
        return {
            'short_name': self.short_name,
            'long_name': self.long_name,
            'data_type': data_type,
            'slug': self.slug
        }
        
    def conversion_factor(self, to_unit):
        if self == to_unit:
            # "No conversion needed, %s and %s are the same units" % (self, to_unit)
            return 1
        if to_unit is None:
            # to_unit is None, Field has no units defined! assume no conversion possible
            return 1
        try:
            uc = UnitConversion.objects.get(from_unit=self, to_unit=to_unit)
        except UnitConversion.DoesNotExist:
            raise ConversionError("%s to %s ... conversion factor not specified in UnitConversion table" % (self, to_unit))

        return uc.factor

    def save(self, *args, **kwargs):
        self.slug = slugify(self.long_name + '_' + self.short_name)
        super(Unit, self).save(*args, **kwargs)
        
    @classmethod
    def get_conversion_factor(cls, from_unit_slug, to_unit_slug):
        key = 'unit_from_%s_to_%s' % (from_unit_slug, to_unit_slug)     #CACHE_KEY  --  conversion factor by to/from units
        factor = cache.get(key)
        if not factor:    
            from_unit = cls.objects.get(slug=from_unit_slug)
            to_unit = cls.objects.get(slug=to_unit_slug)
            try:
                factor = from_unit.conversion_factor(to_unit)
                cache.set(key, factor, settings.CACHE_TIMEOUT)
            except UnitConversion.DoesNotExist:
                raise ConversionError("%s to %s ... conversion factor not specified in UnitConversion table" % (from_unit_slug, to_unit_slug))
                factor = None
        return factor

    class Meta:
        ordering = ['long_name']
        

class UnitConversion(models.Model):
    from_unit = models.ForeignKey(Unit, related_name="from_unit")
    to_unit = models.ForeignKey(Unit, related_name="to_unit")
    factor = models.FloatField()


class Download(models.Model):
    label = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    file_prefix = models.CharField(max_length=80)
    filter_string = models.TextField()
    pretty_print = models.BooleanField()
    auto_generate = models.BooleanField(default=True)
    thefile = models.FileField(upload_to="WCGA_downloads", null=True, blank=True)

    def __unicode__(self):
        return self.label

    @property
    def filename(self):
        timestamp = time.strftime("%Y-%m-%d")
        return "%s_%s.csv" % (self.file_prefix, timestamp)

    @property
    def url(self):
        params = []
        if self.pretty_print:
            params.append("pprint=True")
        params.append("filename=%s" % self.file_prefix)
        params.append("filter=%s" % self.filter_string)
        url = '/events/download.csv?' + "&".join(params)
        return url


class Organization (models.Model):
    orgname = models.TextField()
    url = models.TextField(blank=True, null=True)
    address = models.TextField()
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    scope = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User)
    slug = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.orgname
        
    class Meta:
        ordering = ['orgname']

    
    def get_absolute_url(self):
        return "/organization/%s" % self.slug

    def get_data_url(self):
        return "/events#organization=%s" % self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.orgname)
        super(Organization, self).save(*args, **kwargs)

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
        
class DisplayCategory(models.Model):
    name = models.TextField()
    display_order = models.IntegerField()
    
    class Meta:
        ordering = ['display_order']
    
    def __unicode__(self):
        return self.name
        
class Field (models.Model):
    unit_id = models.ForeignKey(Unit, blank=True, null=True) 
    internal_name = models.TextField(unique=True)
    datatype = models.ForeignKey(DataType, default=8)
    minvalue = models.IntegerField(blank=True, null=True)
    maxvalue = models.IntegerField(blank=True, null=True)
    default_value = models.TextField(blank=True, null=True)  #TODO: What type should this be? Should it be part of Unit? FieldValue?
    description = models.TextField(blank=True, null=True, default=None)
    label = models.TextField(blank=True, null=True, default=None)
    display_category = models.ForeignKey(DisplayCategory, blank=True, null=True)
    
    def __unicode__(self):
        return self.internal_name

    @classmethod
    def toFieldsDict(cls):
        fields_dict = {}
        for field in cls.objects.all():
            fields_dict[field.internal_name] = field.toDict
        
        return fields_dict
        
    @property
    def toDict(self):
        key = 'field_%s' % self.id        #CACHE_KEY  --  field details by field
        dict = cache.get(key)
        if not dict:
            if self.unit_id:
                unit = self.unit_id.toDict
            else:
                unit = {
                    'short_name':'',
                    'long_name': '',
                    'slug': '',
                    'datatype': {
                        'name' : '',
                        'aggregatable': ''
                    }
                }
            if self.display_category:
                display_category = {
                    'name':self.display_category.name,
                    'display_order': self.display_category.display_order
                }
            else:
                display_category = {
                    'name': '',
                    'display_order' : 10000
                }
            
            dict =  {
                'name': self.internal_name,
                'label': self.label,
                'type': self.datatype.name,
                'unit': unit,
                'datatype': {
                    'aggregatable': self.datatype.aggregatable,
                    'name': self.datatype.name
                },
                'display_category': display_category
            }
            cache.set(key, dict, settings.CACHE_TIMEOUT)
            
        return dict
        
    def save(self, *args, **kwargs):
        if self.id:
            # invalidate/clear all cached data associated with this field
            keys = [
                'field_%s' % self.id
            ]
            for key in keys:
                cache.delete(key)
            
        super(Field, self).save(*args, **kwargs)
        
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
    year_started = models.IntegerField(null=True, blank=True, default=None)
    # media_id = models.ForeignKey(Media, blank=True, null=True)
    field = models.ManyToManyField(Field, through='DataSheetField')
    type_id = models.ForeignKey(EventType, null=True, default=None)
    sheet_description = models.TextField(blank=True, null=True, default=None)
    protocol_description = models.TextField(blank=True, null=True, default=None)
    slug = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.created_by.orgname + ' ' + str(self.year_started) + ' ' + self.sheetname
        
    class Meta:
        ordering = ['sheetname']
    

    def save(self, *args, **kwargs):
        self.slug = slugify(self.created_by.orgname + '_' + str(self.year_started) + '_' + self.sheetname)
        super(DataSheet, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "/datasheet/%s/" % self.slug

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
        datasheetfields = []
        for field in self.datasheetfield_set.all():
            
            if field.field_id.unit_id:
                field_unit = field.field_id.unit_id.short_name
            else:
                field_unit = ''
            if field.grouping:
                grouping = field.grouping.name
            else:
                grouping = ''
            
            datasheetfields.append({
                'field': {
                    'id': field.field_id.id,
                    'name': field.field_id.internal_name,
                    'label': field.field_id.label,
                    'datatype': {
                        'name':field.field_id.datatype.name,
                        'aggregatable':field.field_id.datatype.aggregatable
                    },
                    'unit': {
                        'short_name': field_unit
                    }
                },
                'field_name': field.field_name,
                'print_name': field.print_name,
                'unit': {
                    'short_name':field.unit_id.short_name
                },
                'grouping': grouping,
                'required': field.required
            })
            
        ds_dict = {
            'name': self.sheetname,
            'start_date': self.year_started,
            'id': self.id,
            'event_type':type,
            'datasheetfields': datasheetfields,
            'slug': self.slug,
            'url': '/datasheet/'+self.slug
        }
        return ds_dict
    
class DataSheetField (models.Model):
    field_id = models.ForeignKey(Field)
    sheet_id = models.ForeignKey(DataSheet)
    field_name = models.TextField()
    print_name = models.TextField(blank=True, null=True)
    unit_id = models.ForeignKey(Unit, null=True, default=None)
    grouping = models.ForeignKey(Grouping, null=True, blank=True)   #TODO: Name 'category' already claimed. Maybe 'group' or 'subgroup'?
    answer_options = models.ManyToManyField(AnswerOption, help_text='if a list question, multi-select valid responses', blank=True, null=True)
    required = models.BooleanField(default=False)
    
    def __unicode__(self):
        return "%s-%s-%s" % (self.field_name, self.sheet_id.sheetname, self.field_id.internal_name)
        
    class Meta:
        ordering = ['field_name', 'sheet_id__sheetname', 'field_id__internal_name']
    
class Project (models.Model):
    projname = models.TextField(unique=True)
    organization = models.ManyToManyField(Organization, through='ProjectOrganization')
    website = models.TextField(blank=True, null=True)
    contact_name = models.TextField(blank=True, null=True)
    contact_title = models.TextField(blank=True, null=True)
    contact_email = models.TextField(blank=True, null=True)
    contact_phone = models.TextField(blank=True, null=True)
    active_sheets = models.ManyToManyField(DataSheet, through='ProjectDataSheet')
    slug = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.projname
        
    class Meta:
        ordering = ['projname']

    def get_absolute_url(self):
        return "/project/%s/" % self.slug

    def get_data_url(self):
        return "/events#project=%s" % self.slug


    def save(self, *args, **kwargs):
        self.slug = slugify(self.projname)
        super(Project, self).save(*args, **kwargs)

    @property
    def toDict(self):
        datasheets = [datasheet.toDict for datasheet in self.active_sheets.all()]
        proj_dict = {
            'name': self.projname,
            'datasheets': datasheets,
            'get_absolute_url': self.get_absolute_url()
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
        key = 'statecache_%s' % self.id     #CACHE_KEY -- Sites by state
        res = cache.get(key)
        if res == None:
            stateabr = State.objects.get(name=self).initials
            counties = [county.name for county in County.objects.filter(stateabr=stateabr)]
            counties_list = []
            for county in counties:
                if settings.DEMO:
                    sites1 = Site.objects.filter(state=self, county=county)
                    sites2 = Site.objects.filter(state=self, county=county+' County')
                else:
                    sites1 = Site.objects.filter(state=self, county=county, transaction__status = "accepted")
                    sites2 = Site.objects.filter(state=self, county=county+' County', transaction__status = "accepted")
                all_sites = sites1 | sites2
                sites = [x.toDict for x in all_sites]
                county_dict = { 'name': county, 'sites': sites }
                counties_list.append(county_dict)
            res = {
                'name': self.name,
                'initials': self.initials,
                'counties': counties_list
            }
            cache.set(key, res, settings.CACHE_TIMEOUT)
        return res
        
    @property
    def toSimpleDict(self):
        return {
            'name': self.name,
            'initials': self.initials,
            'type': 'state',
        }
        
class UserTransaction (models.Model):
    StatusChoices = (
        ('new', 'new'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected')
    )
    submitted_by = models.ForeignKey(User)
    created_date = models.DateTimeField(auto_now_add = True, default=datetime.datetime.now())
    status = models.CharField(max_length=30, choices=StatusChoices, default='new', blank=True)
    organization = models.ForeignKey(Organization, blank=True, null=True)
    project = models.ForeignKey(Project, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)


    @property
    def toDict(self):    
        key = 'transaction_%s' % self.id        #CACHE_KEY  --  transaction details by transaction
        res = cache.get(key)
        pacific = timezone('US/Pacific')
        
        if not res:
    
            events_count = Event.objects.filter(transaction=self).count()
            sites_count = Site.objects.filter(transaction=self).count()
            
            site_transaction_dependencies = []
            if events_count > 0:
                for event in Event.objects.filter(transaction=self):
                    if not event.site.transaction == self and not event.site.transaction.status == "accepted":
                        if not event.site.transaction.id in site_transaction_dependencies:
                            site_transaction_dependencies.append(event.site.transaction.id)
            
            if self.organization:
                orgname = self.organization.orgname
            else:
                orgname = None
            if self.project:
                projname = self.project.projname
            else:
                projname = None
            
            res = {
                'id': self.id,
                'username': self.submitted_by.username,
                'organization': orgname,
                'project': projname,
                'timestamp': self.created_date.astimezone(pacific).strftime('%m/%d/%Y %H:%M'),
                'status': self.status,
                'id': self.id,
                'events_count': events_count,
                'sites_count': sites_count,
                'site_dependencies': site_transaction_dependencies,
                'reason': self.reason
            }
            cache.set(key, res, settings.CACHE_TIMEOUT)
        return res
    
    def update(self):
        #Clear caches affected by this update
        keys = ['transaction_%s' % self.id]
        states = []
        for site in Site.objects.filter(transaction=self):
            if not site.state.id in states:   
                states.append(site.state.id)
        for st_id in states:
            keys.append('statecache_%s' % st_id)
        for key in keys:
            cache.delete(key)
        
    def __unicode__(self):
        return "%s, %s" % (self.submitted_by, self.created_date.isoformat())
                
class Site (models.Model):
    sitename = models.TextField(blank=True, null=True)
    state = models.ForeignKey(State)
    county = models.TextField(blank=True, null=True)
    geometry = models.PointField(srid=settings.SERVER_SRID, null=True, blank=True)
    transaction = models.ForeignKey(UserTransaction, null=True, default = None)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return unicode(self.sitename)
        
    @property
    def countyDict(self):
        if settings.DEMO:
            sites = [ site.toDict for site in Site.objects.filter(county = self.county)]
        else:
            sites = [ site.toDict for site in Site.objects.filter(county = self.county, transaction__status="accepted")]
        if self.county:
            county = self.county
        else:
            county = ''
        county_dict = {
            'name': county.replace(" County", ""),
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
            'county': county.replace(" County", "")
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
        ('new', 'new'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected')
    )
    transaction = models.ForeignKey(UserTransaction)
    datasheet_id = models.ForeignKey(DataSheet)
    proj_id = models.ForeignKey(Project)
    cleanupdate = models.DateField(default=datetime.date.today())
    site = models.ForeignKey(Site)
    dup = models.IntegerField(default=0)
    objects = models.GeoManager()
    # submitted_by = models.ForeignKey(User, null=True, blank=True, default=None)
    # status = models.CharField(max_length=30, choices=StatusChoices, default='New', blank=True)
    
    def __unicode__(self):
        return "%s-%s-%s" % (self.proj_id.projname, self.site.sitename, self.cleanupdate.isoformat())
        
    def get_fields(self):
        return[(field.name, field.value_to_string(self)) for field in Event._meta.fields]
        
    @classmethod
    def filter(cls, filters, bbox=None):
        event_types = []
        site_filters = []
        date_filters = []
        org_filters = []
        proj_filters = []
        transaction_filters = []
        field_filters = []
        point = None
        # bbox_filter = False
        if filters == None:
            filters = []
        for filter in filters:
            if filter['type'] == 'event_type':
                event_types.append(filter['value'])
            #datepicker sends 1969 as null date              
            elif filter['type'] == 'toDate' or filter['type'] == 'fromDate':
                date_filters.append(filter)
            elif filter['type'] == 'organization':
                org_filters.append(filter)
            elif filter['type'] == 'project':
                proj_filters.append(filter)
            elif filter['type'] == 'transaction':
                transaction_filters.append(filter)
            elif filter['type'] == 'field':
                field_filters.append(filter)
            elif filter['type'] == 'point' or filter['type'] == 'report':
                pass
            else:
                site_filters.append(filter)
        
        if event_types == []:
            event_types.append('all')
        for event_type in event_types:
            if bbox and event_type == 'all':
                geom = Polygon.from_bbox(bbox)
                events = cls.objects.filter(site__geometry__contained=geom)
            elif event_type == 'all':
                events = cls.objects.all()
            else:
                if bbox:
                    geom = Polygon.from_bbox(bbox)
                    events = cls.objects.filter(site__geometry__contained=geom, datasheet_id__type_id__type = event_type)
                else:
                    events = cls.objects.filter(datasheet_id__type_id__type = event_type)
            if site_filters == []:
                filtered_events = events
            else:
                filtered_events = None
            for filter in site_filters:
                if filter['type'] == "county":
                    res = events.filter(site__county=filter['value'], site__state__name=filter['state'])
                    res_county = events.filter(site__county=filter['value'] + ' County', site__state__name=filter['state'])
                    res = res | res_county
                    print len(res)
                if filter['type'] == "state":
                    res = events.filter(site__state__name=filter['value'])
                if filtered_events:
                    filtered_events = filtered_events | res
                else:
                    filtered_events = res
            for filter in proj_filters:
                filtered_events = filtered_events.filter(proj_id__slug=filter['value'])
            for filter in field_filters:
                filtered_events = filtered_events.filter(datasheet_id__field__internal_name=filter['value'])
            for filter in org_filters:
                filtered_events = filtered_events.filter(proj_id__organization__slug=filter['value'])
            for filter in date_filters:
                if filter['type'] == 'toDate':
                    filtered_events = filtered_events.filter(cleanupdate__lte=datetime.datetime.strptime(filter['value'], '%m/%d/%Y'))
                    print "To Date %s " % datetime.datetime.strptime(filter['value'], '%m/%d/%Y')
                if filter['type'] == 'fromDate':
                    filtered_events = filtered_events.filter(cleanupdate__gte=datetime.datetime.strptime(filter['value'], '%m/%d/%Y'))
                    print "From Date %s " % datetime.datetime.strptime(filter['value'], '%m/%d/%Y')
            for filter in transaction_filters:
                filtered_events = filtered_events.filter(transaction=filter['value'])
        # if bbox_filter:
            # filtered_events = filtered_events.filter(site__geometry__contained=geom)

        return filtered_events
        
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
        for fval in fvals.order_by('field_id__display_category__display_order'):
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
                        value = '0'
                except ValueError:
                    pass
            if unit == 'Text':
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
        key = 'event_%s_eventdict' % self.id        #CACHE_KEY  --  Event details by event
        d = cache.get(key)

        if not d:
            proj = self.proj_id
            d = {
                "site": self.site.toDict,
                "project": {
                    "name": proj.projname,
                    "url": proj.get_absolute_url()
                },
                "id": self.id,
                "datasheet": self.datasheet_id.toDict,
                "organization": {
                    "name": proj.projectorganization_set.order_by('-is_lead')[0].organization_id.orgname
                },
                "date" : self.cleanupdate.strftime('%m/%d/%Y')
            } 
            cache.set(key, d, settings.CACHE_TIMEOUT)

        return d

    def toValuesDict(self, convert_units=True):
        """
        Returns a dict of field values. 
        Handles unit conversions between datasheet and internal field.
        Handles converting string to appropriate values (float/int/date/etc)
        TODO Tuples are keys    
        TODO option to convert units or not
        {
          ('internal_field_name','label', 'units'): value_with_converted_units,
        }
        """
        if convert_units:  
            unit_handler = "convert"
        else:
            unit_handler = "raw"

        key = 'event_%s_valuedict_%s' % (self.id, unit_handler)     #CACHE_KEY  --  field values by event
        d = cache.get(key)
        if not d:
            qs = FieldValue.objects.filter(event_id = self) 
            d = {}
            for fv in qs:
                iname = fv.field_id.internal_name
                label = fv.field_id.label
                if convert_units:  
                    units = fv.to_unit_name
                    val = fv.converted_value
                else:
                    units = fv.from_unit_name
                    val = fv.field_value
                if val == 'None':
                    val = None
                d[(iname,label,units)] = val

            cache.set(key, d, settings.CACHE_TIMEOUT)
        return d
        
        
        
    def save(self, *args, **kwargs):
        if self.id:
            site_trans_id = self.site.transaction.id
            # invalidate/clear all cached data associated with this event
            keys = [
                'event_%s_eventdict' % self.id,
                'event_%s_valuedict_convert' % self.id,
                'event_%s_valuedict_raw' % self.id,
                'event_%s_geocache' % self.id,
                'transaction_%s' % site_trans_id
            ]
            for key in keys:
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
        
    @property
    def to_unit_name(self):
        try:
            x = self.to_unit.short_name
        except AttributeError:
            x = None
        return x

    @property
    def from_unit_name(self):
        try:
            x = self.from_unit.short_name
        except AttributeError:
            x = None
        return x

    @property
    def to_unit(self):
        return self.field_id.unit_id

    @property
    def from_unit(self):
        try:
            unit = self.field_id.datasheetfield_set.get(sheet_id=self.event_id.datasheet_id).unit_id
        except:
            unit = None
        return unit


    @property
    def converted_value(self, to_unit=None):
        ''' TODO use some thing like
           converted_value = datasheet_units.factor(desired_units)
        where the factor method of a unit will return the multiplier required to go from it to the desired units
        '''
        try:
            orig_val = float(self.field_value)
        except ValueError:
            # unless its numeric, just pass it along
            return self.field_value

        try:
            if to_unit == None:
                factor = self.from_unit.conversion_factor(self.to_unit)
            else:
                factor = self.from_unit.conversion_factor(to_unit)
        except (AttributeError): #from_unit is None
            factor = 1  # TODO maybe we don't want to fail silently here! 

        converted_value = factor * orig_val

        # cast to int if needed
        if orig_val % 1 == 0 and factor == 1:
            converted_value = int(converted_value)

        return converted_value

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
    
    def __unicode__(self):
        return "%s" % self.name

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
