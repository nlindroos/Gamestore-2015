from django.conf.urls import *
from store.api.views import *

urlpatterns = patterns('',
    # MG: hopefully these patters are not too confusing... (they should work though)
    #
    # Basically: dev, name and tagged are all optional and can appear in any order (meaning that there are 6 combinations, thus the six patterns below).
    # Arguments of the named groups (?P<groupname>) get passed tp api_view as keyword arguments.
    #
    # Note that this regex expects only ascii characters in game names, dev names and tags (which should be good practice for URLs anyway).
    #
    url(r'^games(?:/tagged/(?P<tags>[A-Za-z0-9_|*]+))?(?:/dev/(?P<devs>[A-Za-z0-9_|*]+))?(?:/name/(?P<names>[A-Za-z0-9_|*]+))?$', api_view),
    url(r'^games(?:/tagged/(?P<tags>[A-Za-z0-9_|*]+))?(?:/name/(?P<names>[A-Za-z0-9_|*]+))?(?:/dev/(?P<devs>[A-Za-z0-9_|*]+))?$', api_view),
    url(r'^games(?:/name/(?P<names>[A-Za-z0-9_|*]+))?(?:/tagged/(?P<tags>[A-Za-z0-9_|*]+))?(?:/dev/(?P<devs>[A-Za-z0-9_|*]+))?$', api_view),
    url(r'^games(?:/name/(?P<names>[A-Za-z0-9_|*]+))?(?:/dev/(?P<devs>[A-Za-z0-9_|*]+))?(?:/tagged/(?P<tags>[A-Za-z0-9_|*]+))?$', api_view),
    url(r'^games(?:/dev/(?P<devs>[A-Za-z0-9_|*]+))?(?:/name/(?P<names>[A-Za-z0-9_|*]+))?(?:/tagged/(?P<tags>[A-Za-z0-9_|*]+))?$', api_view),
    url(r'^games(?:/dev/(?P<devs>[A-Za-z0-9_|*]+))?(?:/tagged/(?P<tags>[A-Za-z0-9_|*]+))?(?:/name/(?P<names>[A-Za-z0-9_|*]+))?$', api_view),
)