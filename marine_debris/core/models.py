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
from django.core.exceptions import ValidationError
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
        """Save changes to the organization. 
        Also, invalidate any cached items related to this instance. 
        """
        self.slug = slugify(self.orgname)
        super(Organization, self).save(*args, **kwargs)
    
    @property
    def toDict(self):
        projects = [p.toDict for p in self.project_set.all()]
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
            if self.datatype:
                datatype = {
                    'aggregatable': self.datatype.aggregatable,
                    'name': self.datatype.name
                }
            else:
                datatype = {
                    'aggregatable': False,
                    'name': ''
                }
            
            dict =  {
                'id': self.id,
                'name': self.internal_name,
                'label': self.label,
                'type': self.datatype.name,
                'unit': unit,
                'datatype': datatype,
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


    def fieldnames(self):
        """Return list of field names associated with this datasheet. 
        """
        return self.datasheetfield_set.values_list('field_name', flat=True)

    @property
    def internal_fieldname_lookup(self):
        """
        returns 
        {
            'Internal_Name': 'Datasheet Field Name',
            .....
        }
        """
        return dict([(x.field_id.internal_name, x.field_name) for x in self.datasheetfield_set.select_related().all()])

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
        

    def required_fieldnames(self):
        """
        Collects the fieldnames for required fields of two types:
         - globally required in settings
         - required per datasheet
        """
        cache_key = '%s-%d.required_fieldnames' % (self.__class__.__name__, self.pk)
        result = cache.get(cache_key)
        if result:
            return result
        
        # global
        required_fieldnames = [v['field_name'] 
                               for k, v in self._required_global_field_names().iteritems()]

        # per datasheet
        ds_req_fields = self.datasheetfield_set.filter(required=True)
        for rf in ds_req_fields:
            fieldname = rf.field_name
            if fieldname not in required_fieldnames:
                required_fieldnames.append(fieldname)

        cache.set(cache_key, required_fieldnames)
        return required_fieldnames

    def _required_global_field_names(self):
        """Compute and cache the global required field names dict for this data 
        sheet. Raise a DataSheetError if this data sheet doesn't have the 
        correct required fields. 
        
        Returns {
            'field key': {                  # key as defined in settings.REQUIRED_FIELDS
                'internal_name': <...>,     # Field.internal_name
                'field_name': <...>,        # DataSheetField.field_name, also bulk CSV upload column name
            }
        }
        """
        cache_key = '%s-%d.required_global_field_names' % (self.__class__.__name__, self.pk)
        result = cache.get(cache_key)
        if result:
            return result
        
        req_fields = settings.REQUIRED_FIELDS[self.site_type] 
        field_names = {}
        for key, internal_name in req_fields.items():
            try:
                dsf = self.datasheetfield_set.get(field_id__internal_name=internal_name)
            except DataSheetField.DoesNotExist:
                raise DataSheetError("DataSheet (id=%d) should have a field with internal_name of '%s'" % (self.pk, internal_name,))
            field_names[key] = {'internal_name': internal_name, 'field_name': dsf.field_name}

        cache.set(cache_key, field_names)
        return field_names

    @property
    def site_type(self):
        if self.site_based:
            return "site-based"
        else:
            return "coord-based"


    def is_valid(self):
        req_fields = settings.REQUIRED_FIELDS[self.site_type] 

        # fetch the ID's of the required fields
        req_field_ids = Field.objects.filter(internal_name__in=req_fields.values())
        req_field_ids = req_field_ids.values_list('pk', flat=True)
        req_field_ids = set(req_field_ids)
        
        # fetch the matching field IDs in the DataSheet's field list
        ds_field_ids = self.datasheetfield_set.filter(field_id__in=req_field_ids)
        ds_field_ids = ds_field_ids.values_list('field_id', flat=True)
        ds_field_ids = set(ds_field_ids)
        
        missing_ids = req_field_ids - ds_field_ids
        if missing_ids: 
            # the original code only presented one error (the first), duplicate
            # that here with set.pop()
            missing_fields = Field.objects.filter(pk__in=missing_ids)
            missing_fields = missing_fields.values_list('internal_name', flat=True)
            s = "DataSheet (id=%d) is missing required fields %s"
            s = s % (self.pk, ', '.join(missing_fields))
            return (False, s)

        return (True, "Valid")

    @property
    def site_based(self):
        if self.type_id:
            use_sites = self.type_id.display_sites
        else:
            use_sites = True #default
        return use_sites


    @property
    def toDict(self):
        if self.type_id:
            type = self.type_id.type
        else:
            type = 'None'
        datasheetfields = []
        # for dsfield in self.datasheetfield_set.all():
        #     datasheetfields.append(dsfield.toDict())
            
        ds_dict = {
            'id': self.id,
            'name': self.sheetname,
            'start_date': self.year_started,
            'id': self.id,
            'event_type':type,
            # 'datasheetfields': datasheetfields,
            # nothing else in this program seems to use datasheetfields; 
            # including it costs about 1350 queries and 220 KB more data. 
            # just set to None
            'datasheetfields': None,
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
        
    def toDict(self):
    
        if self.grouping:
            grouping = self.grouping.name
        else:
            grouping = ''
            
        if self.unit_id:
            unit = {
                'short_name': self.unit_id.short_name
            }
        else:
            unit = {
                'short_name': ''
            }
    
        dict = {
            'field': self.field_id.toDict,
            'field_name': self.field_name,
            'print_name': self.print_name,
            'unit': unit,
            'grouping': grouping,
            'required': self.required
        }
        return dict
        
    class Meta:
        ordering = ['field_name', 'sheet_id__sheetname', 'field_id__internal_name']
        
    def clean(self):
        if self.unit_id:
            if self.field_id.unit_id:
                if self.unit_id.data_type:
                    if self.field_id.unit_id.data_type:
                        if not self.unit_id.data_type.name == self.field_id.unit_id.data_type.name:
                            raise ValidationError('This unit id (%s) is not compatible with the field\'s unit id (%s).' % (self.unit_id.long_name,self.field_id.unit_id.long_name))
                    else:
                        raise ValidationError('The field id specified has the unit \'%s\' which does not have a data type assigned. Please update the field\'s unit before saving this data sheet.' % self.field_id.unit_id.long_name)
                else:
                    raise ValidationError('The unit id specified (%s) does not have a data type assigned. Please update the unit before saving this data sheet.' % self.unit_id.long_name)
            else:
                raise ValidationError('The specified field id does not have a unit id assigned. Please assign a unit id to %s before updating this datasheet.' % self.field_id.internal_name)
        else:
            raise ValidationError('Please assign a unit to this data sheet field.')
    
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

class EventSearchDerelictGearManager(models.Manager):
    query = '''
select 
    fv.id as field_value_id,
    f.internal_name as internal_name,
    ST_AsGeoJSON(s.geometry, 15, 0) as geometry,
    'Derelict Gear Removal' as type,
    'count' as unit,
    fv.field_value as field_value,
    1 as field_value_float,
    e.cleanupdate as cleanupdate,
    s.sitename as sitename,
    e.id as event_id

from 
    core_event e
    join core_datasheet ds on e.datasheet_id_id = ds.id
    join core_site s on e.site_id = s.id
    join core_usertransaction ut on e.transaction_id = ut.id
        join core_fieldvalue fv on e.id = fv.event_id_id
            join core_field f on fv.field_id_id = f.id

where
    ut.status = 'accepted'
and ds.type_id_id = 2
and f.internal_name = 'DG_Debris_Type'
'''
    def get_queryset(self, *args, **kwargs):
        raise Exception("You can't query this manager that way; use fetch()")
    
    all = get_queryset
    filter = get_queryset
    exclude = get_queryset
    

    def fetch(self, from_=None, to=None):
        """Get data, optionally filtering by date. 
        The current method of date paramters allows PGSQL date expressions to
        leak through, such as 'NOW', or '2015-1-1'
        This isn't ideal.
        """
        constraints = []
        params = []
        if from_:
            constraints.append("and e.cleanupdate > %s")
            params.append(from_)
        
        if to: 
            constraints.append("and e.cleanupdate < %s")
            params.append(to)
        
        query = self.query + '\n'.join(constraints)
        
        return self.raw(query, params)

class EventSearchDerelictGear(models.Model):
    """An UNMANAGED model to interact with a raw query that provides Derelict
    gear data for the map view.
    """
    class Meta:
        managed = False
    
    objects = EventSearchDerelictGearManager()
    
    field_value_id = models.IntegerField(primary_key=True)
    internal_name = models.TextField()  # Field's internal name
    geometry = models.TextField()       # GeoJSON blob (not a GEOSGeometry)
    type = models.TextField()           # Event Type
    unit = models.TextField()           # Name of the field's "Unit"
    field_value = models.TextField()    # the kind of DG, i.e., Gillnet
    field_value_float = models.FloatField(null=True) # field_value cast to a 
                                                     # float when that makes 
                                                     # sense 
    event_id = models.IntegerField()
    cleanupdate = models.DateField()
    sitename = models.TextField()

class EventOntology(models.Model):
    """An UNMANAGED model to interact with the materialized view (actually, it's
    a regularly generated table) to retrieve data from the events.
    
    
    SQL: 
    drop table if exists event_ontology;

create table event_ontology as 
select 
e.id as event_id,
e.cleanupdate,
s.sitename,
t.type,
ST_AsGeoJSON(s.geometry, 15, 0) as geometry,
f.internal_name,
f.label,
f.id field_id,
fu.short_name unit,
fv.field_value,
case when field_value ~ E'^[0-9\.]+$' then
    cast(field_value as float)
else
    NULL
end as field_value_float,
fv.id field_value_id,
ds.id datasheet_id,
dt.name datatype,
dt.aggregatable,
ds.slug datasheet,
p.slug project,
o.slug organization

from 

core_fieldvalue fv 
join core_field f on fv.field_id_id = f.id
    join core_datatype dt on dt.id = f.datatype_id
    join core_unit fu on fu.id = f.unit_id_id
join core_event e on fv.event_id_id = e.id
    join core_site s on e.site_id = s.id -- 442078
join core_usertransaction ut on e.transaction_id = ut.id and ut.status = 'accepted'  -- 439824

    join core_project p on ut.project_id = p.id -- 203731; about half the data was uploaded prior to the usertransaction foreign keys to project and organization, so that data isn't associated with anything (except maybe the user)
        join core_projectdatasheet pds on p.id = pds.project_id_id
        join core_datasheet ds on ds.id = pds.sheet_id_id
        join core_eventtype t on ds.type_id_id = t.id

join core_organization o on ut.organization_id = o.id

where 
field_value <> 'None'
and field_value <> ''
;

alter table event_ontology add column id bigserial primary key;
-- create index field_internal_name_idx on event_ontology (internal_name);
-- create index field_value_idx on event_ontology (field_value);
-- create index field_data on event_ontology(internal_name, field_value);

select count(*) from event_ontology;
    """
    
    class Meta:
        managed = False
        db_table = 'event_ontology'
    
    id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()    # FK to Event
    cleanupdate = models.DateField()
    sitename = models.TextField()
    type = models.TextField()           # Event Type
    geometry = models.TextField()       # GeoJSON blob (not a GEOSGeometry)
    internal_name = models.TextField()  # Field's internal name
    label = models.TextField()          # field's label
    field_id = models.IntegerField()    # FK to Field
    unit = models.TextField()           # Name of the field's "Unit"
    field_value = models.TextField()    # Format-agnostic value field
    field_value_float = models.FloatField(null=True) # field_value cast to a 
                                                     # float when that makes 
                                                     # sense 
    field_value_id = models.IntegerField()  # FK to FieldValue
    datasheet_id = models.IntegerField()    # FK to DataSheet
    datatype = models.TextField()       # Data sheet's datatype
    aggregatable = models.TextField()   # pseudo bool (T or F)
    datasheet = models.TextField()      # Data sheet slug
    project = models.TextField()        # project slug
    organization = models.TextField()   # organization slug


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
    
    def field_values_gen(self):
        """
        Return a generator that yields field keys & values
        """
        fvals = FieldValue.objects.filter(event_id=self)
        lut = self.datasheet_id.internal_fieldname_lookup
        for fval in fvals.iterator():
            key = unicode(lut[fval.field_id.internal_name])
            value = (fval.field_value, fval.field_id.datatype.name)
            yield key, value

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
        dict = cache.get(key)

        if not dict:
            proj = self.proj_id
            dict = {
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
            cache.set(key, dict, settings.CACHE_TIMEOUT)

        return dict

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
        unique_together = (("cleanupdate", "site", "dup"),)
    
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
        except TypeError:
            # Not something that can be converted to float
            return self.field_value
        except ValueError:
            # Unparsable number
            return self.field_value

        try:
            if to_unit == None:
                factor = self.from_unit.conversion_factor(self.to_unit)
            else:
                factor = self.from_unit.conversion_factor(to_unit)
        except (AttributeError, ConversionError): #from_unit is None
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
