from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response

def api_view(request, **kwargs):
    names = kwargs.get('names', None)
    tags = kwargs.get('tags', None)
    devs = kwargs.get('devs', None)
    return HttpResponse('''Welcome to api. Not implemented.
    
--DEBUG--
Arguments passed:
    name: {}
    tagged: {}
    dev: {}.'''.format(names, tags, devs), content_type='text/plain')