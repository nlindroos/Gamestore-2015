from django.conf.urls import *
from store.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gamestore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^login$', login_view),
    url(r'^signup$', signup_view),
    url(r'^games$', games_view),
    url(r'^games/(\w+)$', play_view),
    url(r'^highscores/(\w+)$', highscore_view),
    url(r'^checkout$', checkout_view),
    url(r'^dev$', developer_view),
    url(r'^dev/sales$', devsales_view),
    url(r'^game_api/v1/', include('store.api.urls')),
)
