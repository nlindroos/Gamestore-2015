from django.conf.urls import *
from store.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gamestore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^login/?$', login_view), #'django.contrib.auth.views.login', {'template_name': 'store/login.html'}),
    url(r'^auth/?$', auth_view),
    url(r'^loggedin/?$', loggedin),
    url(r'^logout/?$', logout_view),
    url(r'^signup/?$', signup_view),
    url(r'^signup_success/?$', signup_success_view),
    url(r'^(?:allgames)?/?$', all_games_view),
    url(r'^mygames/?$', my_games_view),
    url(r'^mygames/(\d+)$', play_view),
    url(r'^checkout/?$', checkout_view),
    url(r'^dev/$', developer_view), # NOTE: must use terminating slash for relative urls to work
    url(r'^dev/newgame/?$', dev_new_game_view),
    url(r'^dev/editgame/(\d+)$', dev_game_edit_view),
    url(r'^denied/?$', denied_view),
    url(r'^mygames/(\d+)/save$', gamestate_ajax_view),
    url(r'^mygames/(\d+)/scores$', gamescore_ajax_view),
    url(r'^game_api/v1/', include('store.api.urls')),
)
