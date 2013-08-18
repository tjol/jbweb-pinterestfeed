from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import feed_dispatcher, hosepipe_view

urlpatterns = patterns('',
	url (r'^rss/(?P<user>[^/]*)/?$', feed_dispatcher, name='pinterest-user-feed'),
	url (r'^rss/(?P<user>[^/]*)/(?P<board>[^/]*)/?$', feed_dispatcher, name='pinterest-board-feed'),
)

urlpatterns += format_suffix_patterns (patterns ('',
    url (r'^api/hosepipe/?$', hosepipe_view),
), allowed=['json', 'jsonp', 'api'])
