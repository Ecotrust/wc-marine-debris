# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DataSheetField.required'
        db.add_column('core_datasheetfield', 'required',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DataSheetField.required'
        db.delete_column('core_datasheetfield', 'required')


    models = {
        'core.category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'core.datasheet': {
            'Meta': {'ordering': "['sheetname']", 'object_name': 'DataSheet'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Organization']"}),
            'field': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Field']", 'through': "orm['core.DataSheetField']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Media']", 'null': 'True', 'blank': 'True'}),
            'sheetname': ('django.db.models.fields.TextField', [], {}),
            'year_started': ('django.db.models.fields.IntegerField', [], {})
        },
        'core.datasheetfield': {
            'Meta': {'ordering': "['field_name', 'sheet_id__sheetname', 'field_id__internal_name']", 'object_name': 'DataSheetField'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'field_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Field']"}),
            'field_name': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'print_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sheet_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataSheet']"}),
            'unit_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Unit']", 'null': 'True', 'blank': 'True'})
        },
        'core.event': {
            'Meta': {'ordering': "['proj_id__projname', 'sitename', 'cleanupdate']", 'object_name': 'Event'},
            'city': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cleanupdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.date.today'}),
            'county': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'datasheet_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataSheet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'proj_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Project']"}),
            'sitename': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.EventType']"})
        },
        'core.eventtype': {
            'Meta': {'ordering': "['type']", 'object_name': 'EventType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.TextField', [], {})
        },
        'core.field': {
            'Meta': {'ordering': "['internal_name']", 'object_name': 'Field'},
            'datatype': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'default_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_name': ('django.db.models.fields.TextField', [], {}),
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
            'contact': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orgname': ('django.db.models.fields.TextField', [], {}),
            'phone': ('django.db.models.fields.TextField', [], {})
        },
        'core.project': {
            'Meta': {'ordering': "['projname']", 'object_name': 'Project'},
            'contact_email': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'contact_phone': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Organization']", 'through': "orm['core.ProjectOrganization']", 'symmetrical': 'False'}),
            'projname': ('django.db.models.fields.TextField', [], {}),
            'website': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.projectorganization': {
            'Meta': {'ordering': "['organization_id__orgname', 'project_id__projname']", 'object_name': 'ProjectOrganization'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_lead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organization_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Organization']"}),
            'project_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Project']"})
        },
        'core.unit': {
            'Meta': {'ordering': "['long_name']", 'object_name': 'Unit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.TextField', [], {}),
            'short_name': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['core']