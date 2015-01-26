from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib import auth
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Min, Sum, Avg
from django.contrib.auth.models import Group
from django.core.mail import send_mail

from store.forms import MyRegistrationForm, GameForm
from store.models import *
from hashlib import md5
import re

def is_player(user):
    """
    Utility function.
    
    Args:
        user: a django.contrib.auth.models.User object
    
    Returns true if a user is a player.
    If the user is not a player, returns False.
    If the user is None, returns None.
    """
    if user:
        try:
            user.groups.get(name='Players')
        except:
            return False
        else:
            return True
    
def is_developer(user):
    """
    Utility function.
    
    Args:
        user: a django.contrib.auth.models.User object
    
    Returns true if a user is a developer.
    If the user is not a developer, returns False.
    If the user is None, returns None.
    """
    if user:
        try:
            user.groups.get(name='Developers')
        except:
            return False
        else:
            return True


def denied_view(request):
    """
    Shown whenever access is not allowed.
    """
    return render(request, 'store/denied.html')
    

def login_view(request):
    """
    View for logging in. 
    Redirect to /auth is done by form action attribute (see logn.html).
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect('/loggedin')
    else:
        c = {}
        c.update(csrf(request))
        return render_to_response('store/login.html', c)
    
def auth_view(request):
    """
    View that authenticates users (after a login) and redirects to the appropriate place.
    
    Redirects to:
        /mygames for players
        /dev for developers
        /login for others (meaning that only players and devs can login)
    """
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        if is_player(user):
            return HttpResponseRedirect('/mygames')
        elif is_developer(user):
            return HttpResponseRedirect('/dev')
    return HttpResponseRedirect('/login')

def loggedin(request):
    return render_to_response('store/loggedin.html')
    
def logout_view(request):
    auth.logout(request)
    return render_to_response('store/logout.html')
    
def signup_view(request):
    """
    View that allows creating a new user.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect('/loggedin')
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False  # Disables user account until it is validated by e-mail
            send_mail('Confirm registration', 'Go to this URL to confirm your account: http://localhost:8000/signup_success/'+str(user.pk), 'admin@gamestore.com',
    [user.email], fail_silently=False)
            return HttpResponse("Confirm your registration via e-mail")

    args = {}
    args.update(csrf(request))
    args['form'] = MyRegistrationForm()
    return render_to_response('store/signup.html', args)

def signup_success_view(request, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
        user.is_active = True
        return render_to_response('store/signup_success.html')
    except ObjectDoesNotExist:
        return HttpResponse("Registration failed :(")
        
def all_games_view(request):
    """
    View that lists all available games.
    
    Owned games are marked as owned so they cannot be repurchased.
    """
    games = Game.objects.all()
    if request.user.is_authenticated() and is_player(request.user):
        # players may own games: don't let them buy the same game twice:
        owned_games = list(x.game for x in request.user.ownedgame_set.all())       
        return render(request, 'store/allgames.html', {'games' : games, 'owned' : owned_games})
    # default behaviour for devs and unregistered users:
    return render(request, 'store/allgames.html', {'games' : games, 'owned' : set()})

def game_detailed(request, game):
    """
    Detailed view for a game. Includes highscores and the possibility to purchase the game.
    """
    try:
        g = Game.objects.get(pk=game)
    except:
        raise Http404('Invalid Game ID')

    if request.user.is_authenticated() and is_player(request.user):
        # players may own games: don't let them buy the same game twice:
        owned_games = list(x.game for x in request.user.ownedgame_set.all())       
        return render(request, 'store/gamedetailed.html', {'g' : g, 'owned' : owned_games})
    # default behaviour for devs and unregistered users:
    return render(request, 'store/gamedetailed.html', {'g' : g, 'owned' : set()})
 
@login_required
@user_passes_test(is_player, "/denied")
def my_games_view(request):
    """
    View that lists all games owned by a player.
    User must be a player and logged in.
    """
    owned_games = list(x.game for x in request.user.ownedgame_set.all())
    return render(request, 'store/mygames.html', {'game_set': owned_games})


@login_required
@user_passes_test(is_player, "/denied")
def play_view(request, game):
    """
    View that allows a player to play a game he/she owns.
    User must be a player, must be logged in and must own the game being played.
    
    Args:
        game: primary key of the Game object
    """
    try:
        g = Game.objects.get(pk=game)
    except:
        raise Http404('Invalid Game ID')
    
    # make sure that only owned games are playable:
    try:
        OwnedGame.objects.get(player=request.user.pk, game=game)
    except:
        # no such game or player doesn't own the game
        raise Http404("You don't own this game :(") # maybe redirect to allgames?
        
    return render(request, 'store/playgame.html', {'gamename' : g.title, 'gameurl' : g.url, 'gameid' : game})
        
@login_required
@user_passes_test(is_player, "/denied")
def checkout_view(request):
    """
    View for buying games using the niksula payment service.
    
    User must be logged in as a player who does not own the game being purchased.
    """
    if request.method == 'GET':
        return HttpResponseRedirect('/denied')
    dictator = {}
    game_id = request.POST.get('game_id', '')
    game = Game.objects.get(pk=game_id)
    sid = "wFEit8qsZlbJ"
    secret_key = "cd1da6350bd3226d26927415319d17e1"
    purchase = Purchase(player=request.user, game=game, fee=game.price)
    pid = purchase.pk
    amount = purchase.fee
    dictator['game_title'] = game.title
    dictator['pid'] = pid
    dictator['sid'] = sid
    dictator['price'] = amount
    dictator['success_url'] = 'http://localhost:8000/mygames'
    dictator['cancel_url'] = 'http://localhost:8000/denied'
    dictator['error_url'] = 'http://localhost:8000/denied'
    checksumstr = "pid=%s&sid=%s&amount=%s&token=%s"%(pid, sid, amount, secret_key)
    m = md5(checksumstr.encode("ascii"))
    checksum = m.hexdigest()
    dictator['checksum'] = checksum
    #Dummy implementation
    purchase.save()
    owned = OwnedGame(player=request.user, game=game, game_state="")
    owned.save()
    return render_to_response('store/checkout.html', dictator)
    
@login_required
@user_passes_test(is_developer, "/denied")
def developer_view(request):
    """
    View that lists all games submitted by a developer and shows some relevant stats.
    
    User must be logged in as a developer.
    """
    games = Game.objects.filter(developer=request.user).annotate(Sum('purchase__fee')).annotate(Count('purchase'))
    # TODO: remove prints!!!!
    print(games.query)
    print(list(games))
    
    return render(request, 'store/developer.html', {'games' : games, 'devname' : request.user.username})

@login_required
@user_passes_test(is_developer, "/denied")
def dev_game_edit_view(request, game):
    """
    View that lets a developer edit one of his/her previously submitted games.
    
    User must be logged in as the developer who originally submitted the game.
    
    Args:
        game: primary key of the Game object
    """
    try:
        g = Game.objects.get(developer=request.user, pk=game)
    except:
        raise Http404('')
    
    if request.method == 'POST':
        c = {}
        c.update(csrf(request))     
        f = GameForm(request.POST)
        if f.is_valid():
            g.title = f.cleaned_data['title']
            g.url = f.cleaned_data['url']
            g.price = f.cleaned_data['price']
            g.description = f.cleaned_data['description']
            # NOTE: tags is a list input (name="tags[]")
            g.tags = ",".join(request.POST.getlist('tags[]'))
            g.save()
            c['game'] = g
            return HttpResponseRedirect('/dev')
        else:
            c['game'] = g
            c['form'] = f
            return render(request, 'store/editgame.html', c)
    return render(request, 'store/editgame.html', {'game' : g})
    
@login_required
@user_passes_test(is_developer, "/denied")
def dev_new_game_view(request):
    """
    View that lets a developer submit a new game.
    Very similar to dev_game_edit_view() (and uses the same template).
    
    User must be logged in as a developer.
    """
    if request.method == 'POST':
        c = {}
        c.update(csrf(request))
        f = GameForm(request.POST)
                       
        if f.is_valid():
            g = Game(developer=request.user, 
                     title=f.cleaned_data['title'], 
                     url=f.cleaned_data['url'], 
                     price=f.cleaned_data['price'],
                     description=f.cleaned_data['description'],
                     img_url=f.cleaned_data.get('img_url', None),
                     tags=",".join(request.POST.getlist('tags[]')))
            # NOTE: tags is a list input (name="tags[]")
            g.save()
            return HttpResponseRedirect('/dev')
        else:
            # make a game dict to emulate a Game object and pass it to the template
            # (to fill form values with previous input)
            c['game'] = {'title' : f.data['title'], 'url' : f.data['url'], 'img_url' : f.data.get('img_url', None) , 'price' : f.data['price'], 'description' : f.data['description'], 'get_tags' : request.POST.getlist('tags[]')}
            c['form'] = f
            return render(request, 'store/editgame.html', c)
    return render(request, 'store/editgame.html')

@login_required
@user_passes_test(is_player, "/denied")   
def gamestate_ajax_view(request, game):
    """
    View for AJAX requests for saving/loading a game.
    
    For GET requests, returns the current gamestate (JSON string).
    For POST requests, stores a new game_state (overwrites the current one).
    User must be logged in as a player and must own the game.
    
    Args:
        game: primary key of the Game object
    """
    
    # make sure that only owned games are playable:
    g = None
    try:
        g = OwnedGame.objects.get(player=request.user.pk, game=game)
    except:
        # no such game or player doesn't own the game
        raise Http404('')

    if request.method == "GET":
        return HttpResponse(g.game_state, content_type="application/json")
    
    # not sure if there's any way to prevent people from just POSTing fake gamestates
    elif request.method == "POST":
        # allow AJAX to POST gamestate data
        #   gamestate should be a be a JSON string in a form input called 'gamestate'
        if request.is_ajax():
            try:
                g.game_state = request.POST['gamestate']
            except KeyError:
                return HttpResponse("No game state given, no changes saved")
            else:
                g.save()
                return HttpResponse("Game state saved successfully!", content_type="text/plain")
    raise Http404('')

@login_required     
@user_passes_test(is_player, "/denied")       
def gamescore_ajax_view(request, game):
    """
    View for AJAX requests for sending highscores to the server.
    
    For POST requests, stores a new highscore.
    User must be logged in as a player and must own the game.
    
    Args:
        game: primary key of the Game object
    """
    
    # make sure that only owned games can be saved to:
    g = None
    try:
        g = OwnedGame.objects.get(player=request.user.pk, game=game)
    except:
        # no such game or player doesn't own the game
        raise Http404('')
    if request.method == "POST" and request.is_ajax():
        try:
            score = Highscore(game=Game.objects.get(pk=game), player=request.user, score=request.POST['score'])
        except:
            raise Http404('')
        else:
            score.save()
            return HttpResponse("Highscore saved successfully!", content_type="text/plain")
    else:
        raise Http404('')
        