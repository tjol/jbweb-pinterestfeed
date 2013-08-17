# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Pin'
        db.create_table(u'pinterestfeed_pin', (
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, primary_key=True)),
            ('img_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('youtube_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('caption', self.gf('django.db.models.fields.TextField')()),
            ('pinboard_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('pinboard_title', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
            ('crawled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('found_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'pinterestfeed', ['Pin'])

        # Adding model 'Feed'
        db.create_table(u'pinterestfeed_feed', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('board', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_requested', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
            ('subtitle', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal(u'pinterestfeed', ['Feed'])

        # Adding M2M table for field pins on 'Feed'
        m2m_table_name = db.shorten_name(u'pinterestfeed_feed_pins')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feed', models.ForeignKey(orm[u'pinterestfeed.feed'], null=False)),
            ('pin', models.ForeignKey(orm[u'pinterestfeed.pin'], null=False))
        ))
        db.create_unique(m2m_table_name, ['feed_id', 'pin_id'])


    def backwards(self, orm):
        # Deleting model 'Pin'
        db.delete_table(u'pinterestfeed_pin')

        # Deleting model 'Feed'
        db.delete_table(u'pinterestfeed_feed')

        # Removing M2M table for field pins on 'Feed'
        db.delete_table(db.shorten_name(u'pinterestfeed_feed_pins'))


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
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'primary_key': 'True'}),
            'youtube_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        }
    }

    complete_apps = ['pinterestfeed']