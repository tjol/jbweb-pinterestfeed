# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Pin.source_url'
        db.alter_column(u'pinterestfeed_pin', 'source_url', self.gf('django.db.models.fields.URLField')(max_length=500, null=True))

    def backwards(self, orm):

        # Changing field 'Pin.source_url'
        db.alter_column(u'pinterestfeed_pin', 'source_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True))

    models = {
        u'pinterestfeed.feed': {
            'Meta': {'object_name': 'Feed'},
            'board': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_requested': ('django.db.models.fields.DateTimeField', [], {}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'pins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'feeds'", 'symmetrical': 'False', 'to': u"orm['pinterestfeed.Pin']"}),
            'subtitle': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'pinterestfeed.pin': {
            'Meta': {'object_name': 'Pin'},
            'caption': ('django.db.models.fields.TextField', [], {}),
            'crawled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'found_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'img_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'pinboard_title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'pinboard_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '500', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'primary_key': 'True'}),
            'youtube_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        }
    }

    complete_apps = ['pinterestfeed']