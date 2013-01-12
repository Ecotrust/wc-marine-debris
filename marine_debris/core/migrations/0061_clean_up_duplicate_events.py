# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        
        # count = 0
        matches = []
        for event in orm['core.Event'].objects.all():
            evt_str = str(event.cleanupdate) + '-' + str(event.site) + '-' + str(event.dup)
            if not evt_str in matches:
                event_qs = orm['core.Event'].objects.filter(cleanupdate=event.cleanupdate, site=event.site, dup = event.dup).order_by('transaction__created_date')
                if event_qs.count() > 1:
                    matches.append(evt_str)
                    
                    #Give preference to ICC events
                    
                    icc = orm['core.Project'].objects.filter(projname="International Coastal Cleanup")
                    if icc.count() == 1:
                        icc_events = event_qs.filter(proj_id=icc[0])
                        for evt in event_qs:
                            if not evt in icc_events:
                                print 'deleting event ' + evt_str
                                evt.delete()
                        continue
                            
                    #If no ICC events, or multiple ICC events remain, take the first event created
                            
                    if event_qs.count() > 1:
                        count = 0
                        for evt in event_qs:
                            if not count == 0:
                                print 'deleting event ' + evt_str
                                evt.delete()
                            count = count + 1

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.answeroption': {
            'Meta': {'ordering': "['display_order']", 'object_name': 'AnswerOption'},
            'display_order': ('django.db.models.fields.FloatField', [], {}),
            'eng_text': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.county': {
            'Meta': {'object_name': 'County'},
            'countyfp': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'stateabr': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'statefp': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'core.datasheet': {
            'Meta': {'ordering': "['sheetname']", 'object_name': 'DataSheet'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Organization']"}),
            'field': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Field']", 'through': "orm['core.DataSheetField']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'protocol_description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'sheet_description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'sheetname': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type_id': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['core.EventType']", 'null': 'True'}),
            'year_started': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'core.datasheetfield': {
            'Meta': {'ordering': "['field_name', 'sheet_id__sheetname', 'field_id__internal_name']", 'object_name': 'DataSheetField'},
            'answer_options': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['core.AnswerOption']", 'null': 'True', 'blank': 'True'}),
            'field_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Field']"}),
            'field_name': ('django.db.models.fields.TextField', [], {}),
            'grouping': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Grouping']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'print_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sheet_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataSheet']"}),
            'unit_id': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['core.Unit']", 'null': 'True'})
        },
        'core.datatype': {
            'Meta': {'object_name': 'DataType'},
            'aggregatable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'core.displaycategory': {
            'Meta': {'ordering': "['display_order']", 'object_name': 'DisplayCategory'},
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'core.download': {
            'Meta': {'object_name': 'Download'},
            'auto_generate': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file_prefix': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'filter_string': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'pretty_print': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thefile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'core.event': {
            'Meta': {'ordering': "['proj_id__projname', 'site', 'cleanupdate']", 'unique_together': "(('datasheet_id', 'proj_id', 'cleanupdate', 'site', 'dup'),)", 'object_name': 'Event'},
            'cleanupdate': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 1, 11, 0, 0)'}),
            'datasheet_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataSheet']"}),
            'dup': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proj_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Project']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Site']"}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.UserTransaction']"})
        },
        'core.eventtype': {
            'Meta': {'ordering': "['type']", 'object_name': 'EventType'},
            'display_sites': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {})
        },
        'core.field': {
            'Meta': {'ordering': "['internal_name']", 'object_name': 'Field'},
            'datatype': ('django.db.models.fields.related.ForeignKey', [], {'default': '8', 'to': "orm['core.DataType']"}),
            'default_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'display_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DisplayCategory']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'maxvalue': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'minvalue': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'unit_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Unit']", 'null': 'True', 'blank': 'True'})
        },
        'core.fieldvalue': {
            'Meta': {'ordering': "['event_id', 'field_id__internal_name']", 'object_name': 'FieldValue'},
            'event_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Event']"}),
            'field_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Field']"}),
            'field_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.grouping': {
            'Meta': {'ordering': "['name']", 'object_name': 'Grouping'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'core.media': {
            'Meta': {'ordering': "['proj_id__projname', 'filename']", 'object_name': 'Media'},
            'filename': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proj_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Project']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {})
        },
        'core.organization': {
            'Meta': {'ordering': "['orgname']", 'object_name': 'Organization'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'city': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orgname': ('django.db.models.fields.TextField', [], {}),
            'scope': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'zip': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.project': {
            'Meta': {'ordering': "['projname']", 'object_name': 'Project'},
            'active_sheets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.DataSheet']", 'through': "orm['core.ProjectDataSheet']", 'symmetrical': 'False'}),
            'contact_email': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'contact_phone': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'contact_title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Organization']", 'through': "orm['core.ProjectOrganization']", 'symmetrical': 'False'}),
            'projname': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'slug': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.projectdatasheet': {
            'Meta': {'ordering': "['project_id__projname', 'sheet_id__sheetname']", 'object_name': 'ProjectDataSheet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Project']"}),
            'sheet_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataSheet']"})
        },
        'core.projectorganization': {
            'Meta': {'ordering': "['organization_id__orgname', 'project_id__projname']", 'object_name': 'ProjectOrganization'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organization_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Organization']"}),
            'project_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Project']"})
        },
        'core.site': {
            'Meta': {'unique_together': "(('sitename', 'state', 'county'),)", 'object_name': 'Site'},
            'county': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sitename': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.State']"}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['core.UserTransaction']", 'null': 'True'})
        },
        'core.state': {
            'Meta': {'ordering': "['name', 'initials']", 'unique_together': "(('name', 'initials'),)", 'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initials': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'core.unit': {
            'Meta': {'ordering': "['long_name']", 'object_name': 'Unit'},
            'data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.TextField', [], {}),
            'short_name': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'core.unitconversion': {
            'Meta': {'object_name': 'UnitConversion'},
            'factor': ('django.db.models.fields.FloatField', [], {}),
            'from_unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_unit'", 'to': "orm['core.Unit']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_unit'", 'to': "orm['core.Unit']"})
        },
        'core.usertransaction': {
            'Meta': {'object_name': 'UserTransaction'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 11, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Organization']", 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Project']", 'null': 'True', 'blank': 'True'}),
            'reason': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '30', 'blank': 'True'}),
            'submitted_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['core']
    symmetrical = True
