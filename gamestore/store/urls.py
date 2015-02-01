from django.conf.urls import *
from store.views import *

urlpatterns = patterns('',

    url(r'^login/?$', login_view, name="login"), #'django.contrib.auth.views.login', {'template_name': 'store/login.html'}),
    url(r'^auth/?$', auth_view),
    url(r'^loggedin/?$', loggedin),
    url(r'^logout/?$', logout_view, name="logout"),
    url(r'^signup/?$', signup_view, name="signup"),
    url(r'^signup_success/(\S+)$', signup_success_view),
    url(r'^(?:allgames)?/?$', all_games_view, name="allgames"),
    url(r'^allgames/?(\d+)', game_detailed, name="gamedetailed"),
    url(r'^mygames/?$', my_games_view, name="mygames"),
    url(r'^mygames/(\d+)/?$', play_view, name="play"),
    url(r'^checkout/?$', checkout_view),
    url(r'^confirm_order/(\d+)$', confirm_order_view),
    url(r'^cancel_order/(\d+)$', cancel_order_view),
    url(r'^dev/$', developer_view, name="dev_home"), # NOTE: must use terminating slash for relative urls to work
    url(r'^dev/newgame/?$', dev_new_game_view),
    url(r'^dev/editgame/(\d+)$', dev_game_edit_view),
    url(r'^denied/?$', denied_view, name="denied"),
    url(r'^mygames/(\d+)/save$', gamestate_ajax_view),
    url(r'^mygames/(\d+)/scores$', gamescore_ajax_view),
    url(r'^game_api/v1/', include('store.api.urls')),
)
