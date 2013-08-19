# -*- coding: utf-8 -*-
#
# jbweb-pinterestfeed - Django app that generates Pinterest RSS feeds
# Copyright (C) 2013  Thomas Jollans <t@jollybox.de>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

import re
import urllib2
from datetime import datetime, timedelta

import pytz
import celery
import feedparser
from bs4 import BeautifulSoup
from django.utils import timezone
from celery.utils.log import get_task_logger

from pinterestfeed.models import *

logger = get_task_logger (__name__)

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36'

@celery.task
def fetch_feed (feed_obj):
    orig = feedparser.parse (feed_obj.src_url)

    try:
        orig_updated = datetime (*orig.feed.updated_parsed[:6], tzinfo=pytz.UTC)
        if feed_obj.last_updated and feed_obj.last_updated >= orig_updated:
            return
        
        logger.info ("Updating feed: {0}".format(feed_obj.src_url))

        feed_obj.last_updated = timezone.now ()

        feed_obj.title = orig.feed.title
        feed_obj.subtitle = orig.feed.subtitle
        feed_obj.save()
    except:
        try:
            feed_obj.delete()
        except:
            pass
        finally:
            return

    for entry in orig.entries:
        pin_url = entry.link
        try:
            pin = Pin.objects.get (url=pin_url)
            feed_obj.pins.add (pin)
        except Pin.DoesNotExist:
            pin = Pin (url=pin_url)
            soup = BeautifulSoup (entry.summary)
            pin.pub_date = datetime (*entry.published_parsed[:6], tzinfo=pytz.UTC)
            pin.img_url = soup.find ('img')['src']
            try:
                pin.caption = soup.find_all ('p')[-1].text
            except:
                pin.caption = soup.get_text ()
            pin.save ()
            feed_obj.pins.add (pin)

            scrape_pin.delay (pin)

@celery.task
def scrape_pin (pin):
    request = urllib2.Request (pin.url)
    request.add_header ('User-Agent', USER_AGENT)
    request.add_header ('Accept', 'text/html')

    stream = urllib2.urlopen (request)
    soup = BeautifulSoup (stream)

    # Get basic data

    img_url_elem = soup.find ('meta', {'property': 'og:image'})
    caption_elem = soup.find ('meta', {'property': 'og:description'})
    board_url_elem = soup.find ('meta', {'property': 'pinterestapp:pinboard'})
    board_title_elem = soup.find ('meta', {'property': 'og:title'})
    source_elem = soup.find ('meta', {'property': 'pinterestapp:source'})

    if img_url_elem:
        pin.img_url = img_url_elem['content']
    if caption_elem:
        pin.caption = caption_elem['content']
    if source_elem:
        pin.source_url = source_elem['content']
    if board_url_elem:
        pin.pinboard_url = board_url_elem['content']
    if board_title_elem:
        pin.pinboard_title = board_title_elem['content']

    # Check if it's a YouTube video:
    yt_embed_re = re.compile (r'http://.*youtube.*/embed/([^?/]*)')
    yt_frame = soup.find ('iframe', {'src': yt_embed_re})
    if yt_frame:
        pin.youtube_id = yt_embed_re.match (yt_frame['src']).group (1)

    pin.crawled = True
    pin.save ()

@celery.task
def update_old_feeds (active_hours=25, ttl_minutes=25):
    now = timezone.now ()
    requested_since = now - timedelta (hours=active_hours)
    not_updated_since = now - timedelta (minutes=ttl_minutes)

    for feed in (Feed.objects.filter (last_updated__lt=not_updated_since,
                                     last_requested__gt=requested_since)
                             .order_by ('last_updated')):
        fetch_feed.delay (feed)

@celery.task
def fetch_lost_pins (grace_preriod_minutes=30):
    now = timezone.now ()
    older_than = now - timedelta (minutes=grace_preriod_minutes)

    for pin in Pin.objects.filter (crawled=False, found_at__lt=older_than):
        scrape_pin.delay (pin)
