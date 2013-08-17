from django.conf.urls import patterns, include, url

from .views import feed_dispatcher

urlpatterns = patterns('',
	url (r'^rss/(?P<user>[^/]*)/?$', feed_dispatcher, name='pinterest-user-feed'),
	url (r'^rss/(?P<user>[^/]*)/(?P<board>[^/]*)/?$', feed_dispatcher, name='pinterest-board-feed'),
)
