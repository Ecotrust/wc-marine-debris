# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Unit'
        db.create_table('core_unit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.TextField')()),
            ('long_name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('core', ['Unit'])

        # Adding model 'Organization'
        db.create_table('core_organization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('orgname', self.gf('django.db.models.fields.TextField')()),
            ('contact', self.gf('django.db.models.fields.TextField')()),
            ('phone', self.gf('django.db.models.fields.TextField')()),
            ('address', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('core', ['Organization'])

        # Adding model 'Project'
        db.create_table('core_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('projname', self.gf('django.db.models.fields.TextField')()),
            ('website', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('contact_name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('contact_email', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('contact_phone', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Project'])

        # Adding model 'ProjectOrganization'
        db.create_table('core_projectorganization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Organization'])),
            ('project_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Project'])),
            ('is_lead', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['ProjectOrganization'])

        # Adding model 'Media'
        db.create_table('core_media', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.TextField')()),
            ('filename', self.gf('django.db.models.fields.TextField')()),
            ('proj_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Project'])),
            ('published', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Media'])

        # Adding model 'Category'
        db.create_table('core_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('core', ['Category'])

        # Adding model 'Field'
        db.create_table('core_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Unit'], null=True, blank=True)),
            ('internal_name', self.gf('django.db.models.fields.TextField')()),
            ('datatype', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('minvalue', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('maxvalue', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('default_value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Field'])

        # Adding model 'DataSheet'
        db.create_table('core_datasheet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sheetname', self.gf('django.db.models.fields.TextField')()),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Organization'])),
            ('year_started', self.gf('django.db.models.fields.IntegerField')()),
            ('media_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Media'], null=True, blank=True)),
        ))
        db.send_create_signal('core', ['DataSheet'])

        # Adding model 'DataSheetField'
        db.create_table('core_datasheetfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Field'])),
            ('sheet_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DataSheet'])),
            ('field_name', self.gf('django.db.models.fields.TextField')()),
            ('print_name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('unit_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Unit'], null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Category'], null=True, blank=True)),
        ))
        db.send_create_signal('core', ['DataSheetField'])

        # Adding model 'EventType'
        db.create_table('core_eventtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('core', ['EventType'])

        # Adding model 'Event'
        db.create_table('core_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datasheet_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DataSheet'])),
            ('proj_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Project'])),
            ('type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.EventType'])),
            ('cleanupdate', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('sitename', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('lon', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('county', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Event'])

        # Adding model 'FieldValue'
        db.create_table('core_fieldvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Field'])),
            ('event_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Event'])),
            ('field_value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['FieldValue'])


    def backwards(self, orm):
        # Deleting model 'Unit'
        db.delete_table('core_unit')

        # Deleting model 'Organization'
        db.delete_table('core_organization')

        # Deleting model 'Project'
        db.delete_table('core_project')

        # Deleting model 'ProjectOrganization'
        db.delete_table('core_projectorganization')

        # Deleting model 'Media'
        db.delete_table('core_media')

        # Deleting model 'Category'
        db.delete_table('core_category')

        # Deleting model 'Field'
        db.delete_table('core_field')

        # Deleting model 'DataSheet'
        db.delete_table('core_datasheet')

        # Deleting model 'DataSheetField'
        db.delete_table('core_datasheetfield')

        # Deleting model 'EventType'
        db.delete_table('core_eventtype')

        # Deleting model 'Event'
        db.delete_table('core_event')

        # Deleting model 'FieldValue'
        db.delete_table('core_fieldvalue')


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
            'sheet_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataSheet']"}),
            'unit_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Unit']", 'null': 'True', 'blank': 'True'})
        },
        'core.event': {
            'Meta': {'ordering': "['proj_id__projname', 'sitename', 'cleanupdate']", 'object_name': 'Event'},
            'city': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cleanupdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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