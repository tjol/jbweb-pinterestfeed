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

from datetime import timedelta
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.http import Http404
from django.views.decorators.http import require_safe
from django.http.response import HttpResponse

import django.contrib.syndication.views as syn
from rest_framework.decorators import api_view
from rest_framework.response import Response

from pinterestfeed import models, tasks
from .serializers import PinSerializer

class PinterestFeed (syn.Feed):
    def get_object (self, request, feed):
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
        feed.last_requested = timezone.now ()
        feed.save (update_fields=('last_requested',))
        return feed_view (request, feed=feed)
    except models.Feed.MultipleObjectsReturned:
        models.Feed.objects.filter (user=user, board=board).delete ()
        return feed_dispatcher (request, user, board)
    except models.Feed.DoesNotExist:
        feed = models.Feed.objects.create (user=user, board=board, last_requested=timezone.now ())
        tasks.fetch_feed.delay (feed).wait ()
        try:
            feed = models.Feed.objects.get (user=user, board=board)
        except models.Feed.DoesNotExist:
            raise Http404
        except models.Feed.MultipleObjectsReturned:
            models.Feed.objects.filter (user=user, board=board).delete ()
            return feed_dispatcher (request, user, board)
        else:
            return feed_dispatcher (request, user, board)
        #return HttpResponse ("Request accepted, processing pending",
        #                     content_type="text/plain",
        #                     status=202)


@api_view(['POST'])
def hosepipe_view (request, format=None):
    not_these_urls = set(request.DATA.get('not', []))
    limit = request.DATA.get('limit', 15)

    serializer = PinSerializer ((
            p for p in models.Pin.objects
                                 .filter (crawled=True)
                                 .order_by ('-pub_date')
                                 [:limit]
              if p.url not in not_these_urls),
                        many=True)

    return Response (serializer.data)


@require_safe
def stats (request):
    now = timezone.now ()
    one_hour_ago = now - timedelta (hours=1)
    twentyfour_h_ago = now - timedelta (hours=24)
    fifteen_min_ago = now - timedelta (minutes=30)
    resp = HttpResponse (status=200, content_type='text/plain')
    resp.write ("Total number of feeds: {0}\n".format (models.Feed.objects.count ()))
    resp.write ("Total number of pins: {0}\n".format (models.Pin.objects.count ()))
    resp.write ("Pins not crawled: {0}\n".format (models.Pin.objects.filter (crawled=False).count ()))
    resp.write ("Feeds requested in the last hour: {0}\n".format (models.Feed.objects.filter (last_requested__gte=one_hour_ago).count ()))
    resp.write ("Feeds requested in the 24 hours: {0}\n".format (models.Feed.objects.filter (last_requested__gte=twentyfour_h_ago).count ()))
    resp.write ("Feeds updated in the past 15 minutes: {0}\n".format (models.Feed.objects.filter (last_updated__gte=fifteen_min_ago).count ()))
    return resp

