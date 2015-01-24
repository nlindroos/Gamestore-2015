from django.conf.urls import *
from store.api.views import *

title_pattern = r'(?P<titles>(?:/title/(?:[a-z0-9_*]+))*)'
dev_pattern = r'(?P<developers>(?:/dev/(?:[a-z0-9_*]+))*)'
tag_pattern = r'(?P<tags>(?:/tagged/(?:[a-z0-9_*]+))*)'

urlpatterns = patterns('',
    url(r'^games/$', api_view),
    url(r'^games{}{}{}$'.format(title_pattern, dev_pattern, tag_pattern), api_view),
    url(r'^games{}{}{}$'.format(title_pattern, tag_pattern, dev_pattern), api_view),
    url(r'^games{}{}{}$'.format(dev_pattern, tag_pattern, title_pattern), api_view),
    url(r'^games{}{}{}$'.format(dev_pattern, title_pattern, tag_pattern), api_view),
    url(r'^games{}{}{}$'.format(tag_pattern, dev_pattern, title_pattern), api_view),
    url(r'^games{}{}{}$'.format(tag_pattern, title_pattern, dev_pattern), api_view),
)
# MG: hopefully these patters are not too confusing... (they should work though)
#
# Basically: dev, title and tagged are all optional and can appear in any order 
# (meaning that there are 6 combinations, thus the six patterns).
#
# Arguments of the named groups (?P<groupname>) get passed tp api_view as keyword arguments.
#
# Note that this regex expects only ascii characters in game, dev and tagged
# (which should be good practice for URLs anyway).
#
#
# examples of valid patterns:
# /title/some_title/dev/some_dev/tagged/some_tag
# /title/some_title/title/another_title/tagged/funny/tagged/
# /tagged/fun*/dev/dev1/dev/dev2