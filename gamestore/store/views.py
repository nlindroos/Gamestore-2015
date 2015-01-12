from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib import auth
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm

#from datetime import utcnow
#http://bradmontgomery.blogspot.fi/2009/04/restricting-access-by-group-in-django.html

from store.models import *

def is_player(user):
    if user:
        try:
            user.groups.get(name='Player')
        except:
            return False
        else:
            return True
    
def is_developer(user):
    if user:
        try:
            user.groups.get(name='Developer')
        except:
            return False
        else:
            return True


# Create your views here.

def login_view(request):
    if request.user.is_authenticated():
        return render(request, 'store/loggedin.html')
    else:
        c = {}
        c.update(csrf(request))
        return render_to_response('store/login.html', c)
    
def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return render(request, 'store/mygames.html')
    else:
        return render(request, 'store/login.html')

def loggedin(request):
    return render_to_response('store/loggedin.html')
    
def logout_view(request):
    auth.logout(request)
    return render_to_response('store/logout.html')
    
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():             #TODO: Extend with email validation
            form.save()   
            return HttpResponseRedirect('/signup_success')    
    args = {}
    args.update(csrf(request))
    args['form'] = UserCreationForm()
    return render_to_response('store/signup.html', args)

def signup_success_view(request):
    return render_to_response('store/signup_success.html')
    
def all_games_view(request):
    games = Game.objects.all()
    if request.user.is_authenticated() and is_player(request.user):
        owned_games = set(x.pk for x in OwnedGame.objects.filter(player=request.user.pk))
        return render(request, 'store/allgames.html', {'games' : games, 'owned' : owned_games})
    return render(request, 'store/allgames.html', {'games' : games, 'owned' : set()})
    #return HttpResponse('Welcome to all games. Not implemented')
 
@login_required
@user_passes_test(is_user, denied_view)
def my_games_view(request):
    games = OwnedGame.objects.filter(player=request.user.pk)
    return render(request, 'store/mygames.html', {'games': games})

@login_required
@user_passes_test(is_user, denied_view)
def play_view(request, game):
    """
    Args:
        game: DB primary key of the game
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
@user_passes_test(is_user, denied_view)
def checkout_view(request):
    return HttpResponse('Welcome to checkout. Not implemented')    
    
@login_required
@user_passes_test(is_developer, denied_view)
def developer_view(request):
    return HttpResponse('Welcome to developer. Not implemented')

@login_required
@user_passes_test(is_user, denied_view)   
def gamestate_ajax_view(request, game):
    
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
                g.gamestate = request.POST['gamestate']
            except KeyError:
                return HttpResponse("No game state given, no changes saved")
            else:
                g.save()
                return HttpResponse("Game state saved successfully!", content_type="text/plain")
        else:
            raise Http404('')

@login_required     
@user_passes_test(is_user, denied_view)       
def gamescore_ajax_view(request, game):
    
    # make sure that only owned games can be saved to:
    g = None
    try:
        g = OwnedGame.objects.get(player=request.user.pk, game=game)
    except:
        # no such game or player doesn't own the game
        raise Http404('')
    
    if request.method == "POST" and request.is_ajax():
        try:
            score = Highscore(game=game, player=request.user.pk, score=request.POST['score'])
            score.save()
        except:
            raise Http404('')
    else:
        raise Http404('')
        