from django.conf.urls import *
from store.api.views import *

title_pattern = r'(?P<titles>(?:/title/(?:[^/]+))*)'
dev_pattern = r'(?P<developers>(?:/dev/(?:[^/]+))*)'
tag_pattern = r'(?P<tags>(?:/tagged/(?:[^/]+))*)'
id_pattern = r'(?P<id>(?:/id/(?:\d+))*)'
start_date_pattern = r'((?:/startdate/)(?P<startdate>([^/]*)))' # we validate the date format in view, not in url
end_date_pattern = r'((?:/enddate/)(?P<enddate>([^/]*)))'

urlpatterns = patterns('',
    url(r'^games/$', api_games_view),
    url(r'^games{}/?$'.format(id_pattern), api_games_view),
    url(r'^games{}{}{}/?$'.format(title_pattern, dev_pattern, tag_pattern), api_games_view),
    url(r'^sales/$', api_dev_sales_view),
    url(r'^sales{}{}?{}?/?$'.format(id_pattern.replace('id', 'gameid'), start_date_pattern, end_date_pattern), api_dev_sales_view),
    url(r'^sales{}{}?{}?/?$'.format(title_pattern, start_date_pattern, end_date_pattern), api_dev_sales_view),
    url(r'^help$', api_help_view, name="apihelp")
)
# MG: hopefully these patters are not too confusing... (they should work though)
#
# Arguments of the named groups (?P<groupname>) get passed tp api_view as keyword arguments.
#
# Note that this regex expects only ascii characters in game, dev and tagged
# (which should be good practice for URLs anyway).