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

from django.utils import timezone
from django.core.urlresolvers import reverse
import django.contrib.syndication.views as syn
from django.shortcuts import get_object_or_404
from django.template import Context
from django.template.loader import get_template
from django.http import HttpResponse

from pinterestfeed import models, tasks

class PinterestFeed (syn.Feed):
    def get_object (self, request, feed):
        feed.last_requested = timezone.now ()
        feed.save (update_fields=('last_requested',))
        return feed

    def title (self, feed):
        return feed.title or feed.board or feed.user

    def description (self, feed):
        return u'{0} [IMPROVED FEED]'.format (feed.subtitle or feed.user)

    def link (self, feed):
        return feed.src_url

    def feed_url (self, feed):
        kwargs = {'user': feed.user}
        if feed.board:
            kwargs['board'] = feed.board
            return reverse ('pinterest-board-feed', kwargs = kwargs)
        else:
            return reverse ('pinterest-user-feed', kwargs = kwargs)

    def guid (self, feed):
        return self.feed_url (feed)

    def description (self, feed):
        return feed.subtitle or feed.title or feed.board or feed.user

    def author_link (self, feed):
        return 'http://www.pinterest.com/{0}'.format(feed.user)

    def items (self, feed):
        return feed.pins.order_by ('-pub_date') [:25]

    def item_pubdate (self, pin):
        return pin.pub_date

    def item_description (self, pin):
        template = get_template ("pin.html")
        context = Context ({'pin': pin})
        return template.render (context)

feed_view = PinterestFeed ()

def feed_dispatcher (request, user, board=None):
    try:
        feed = models.Feed.objects.get (user=user, board=board)
        return feed_view (request, feed=feed)
    except models.Feed.DoesNotExist:
        feed = models.Feed (user=user, board=board, last_requested=timezone.now ())
        tasks.fetch_feed.delay (feed).wait ()
        return feed_view (request, feed=feed)
        #return HttpResponse ("Request accepted, processing pending",
        #                     content_type="text/plain",
        #                     status=202)

