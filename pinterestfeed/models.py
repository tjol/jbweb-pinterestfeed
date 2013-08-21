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

__all__ = ['Pin', 'Feed']

from django.db import models


class Pin (models.Model):
    """
    A Pinterest pin
    """
    url = models.URLField (primary_key=True)
    
    img_url = models.URLField ()
    youtube_id = models.CharField (max_length=50, null=True)
    
    source_url = models.URLField (max_length=500, null=True)
    caption = models.TextField ()

    pinboard_url = models.URLField (null=True)
    pinboard_title = models.CharField (max_length=500, null=True)

    crawled = models.BooleanField (default=False)

    pub_date = models.DateTimeField ()
    found_at = models.DateTimeField (auto_now_add=True)

    def get_absolute_url (self):
        return self.url

    def __unicode__ (self):
        return self.caption

    def save (self, *args, **kwargs):
        if self.source_url and len(self.source_url) > 500: # This can happen!
            self.source_url = self.source_url[:500]

        return super (Pin, self).save (*args, **kwargs)


class Feed (models.Model):
    """
    A requested Pinterest feed
    """
    user = models.CharField (max_length=500)
    board = models.CharField (max_length=500, null=True)

    last_updated = models.DateTimeField (null=True)
    last_requested = models.DateTimeField ()

    pins = models.ManyToManyField (Pin, related_name='feeds')

    title = models.CharField (max_length=500, null=True)
    subtitle = models.TextField (null=True)

    @property
    def src_url (self):
        if self.board is None:
            return u'http://pinterest.com/{user}/feed.rss'.format(user=self.user)
        else:
            return u'http://pinterest.com/{user}/{board}/rss'.format(user=self.user,
                                                                       board=self.board)

    def __unicode__ (self):
        return u'{0} ({1})'.format (self.title or self.board or '', self.user)

