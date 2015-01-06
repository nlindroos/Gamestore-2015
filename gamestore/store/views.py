from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response

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
    return HttpResponse('Welcome to login. Not implemented')
    
def signup_view(request):
    return HttpResponse('Welcome to signup. Not implemented')
    
def all_games_view(request):
    return HttpResponse('Welcome to all games. Not implemented')
    
def my_games_view(request):
    return HttpResponse('Welcome to my games. Not implemented')
    
def play_view(request, game):
    return HttpResponse('''Welcome to play. Not implemented

--DEBUG--
You are playing: {}'''.format(game), content_type='text/plain')
        
def checkout_view(request):
    return HttpResponse('Welcome to checkou. Not implemented')    
    
def developer_view(request):
    return HttpResponse('Welcome to developer. Not implemented')