from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from store.models import *

# Create your views here.

def login_view(request):
    '''from django.contrib.auth import authenticate, login

def my_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
        else:
            # Return a 'disabled account' error message
    else:
        # Return an 'invalid login' error message.'''
    return render(request, 'store/login.html')
    
def signup_view(request):
    return HttpResponse('Welcome to signup. Not implemented')
    
def all_games_view(request):
    return HttpResponse('Welcome to all games. Not implemented')
 
#@login_required  
def my_games_view(request):
    return HttpResponse('Welcome to my games. Not implemented')

#@login_required
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
        
#@login_required    
def checkout_view(request):
    return HttpResponse('Welcome to checkout. Not implemented')    
    
#@login_required
def developer_view(request):
    return HttpResponse('Welcome to developer. Not implemented')

#@login_required    
def gamestate_ajax_view(request, game):
    
    # make sure that only owned games are playable:
    g = get_owned_game(request, game)
    try:
        g = OwnedGame.objects.get(player=request.user.pk, game=game)
    except:
        # no such game or player doesn't own the game
        raise Http404('')

    if request.method == "GET":
        return HttpResponse(g.gamestate, content_type="application/json")
    
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
        