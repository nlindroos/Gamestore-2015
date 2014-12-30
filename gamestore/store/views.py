from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response

# Create your views here.

def login_view(request):
    return HttpResponse('Welcome to login. Not implemented')
    
def signup_view(request):
    return HttpResponse('Welcome to signup. Not implemented')
    
def games_view(request):
    return HttpResponse('Welcome to games. Not implemented')
    
def play_view(request, game):
    return HttpResponse('''Welcome to play. Not implemented

--DEBUG--
You are playing: {}'''.format(game), content_type='text/plain')
    
def highscore_view(request, game):
        return HttpResponse('''Welcome to highscore. Not implemented

--DEBUG--
Showing scores for: {}'''.format(game), content_type='text/plain')
    
def checkout_view(request):
    return HttpResponse('Welcome to checkou. Not implemented')    
    
def developer_view(request):
    return HttpResponse('Welcome to developer. Not implemented')
    
def devsales_view(request):
    return HttpResponse('Welcome to developer sales. Not implemented')