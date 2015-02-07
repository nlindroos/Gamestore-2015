from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.db.models import Q
from json import dumps
import re
import datetime
import django.utils.timezone as timez
from django.db.models import Count, Min, Sum, Avg

from store.models import Game, Purchase
from store.views import is_developer, login_only, developers_only


def wildcard_builder(src, attr):
    """
    Given a string, creates a Q object wildcard match.
    
    Attributes:
        src:    The source string possibly containing * wildcards
        attr:   A string: name of the attribute that should be matched
    
    For example:
    
        src = 'test'      ---> attr__iexact : 'test'
        src = '*test'     ---> attr_iendswith : 'test'
        src = 'test*'     ---> attr_istartswith : 'test'
        src = 'te*st'     ---> attr_istartswith : 'te' & attr_iendswith : 'st'
        src = '*test*'    ---> attr_icontains : 'test'
        src = 't*e*st'    ---> attr_istartswith : 't' & attr_icontains : 'e' & attr_iendswith : 'st'
        
    Returns:
        a Q object
    """
    if (src == '*'):
        return Q()
    parts = src.split('*')
    if len(parts) == 1:
        return Q(**{'{}__iexact'.format(attr) : src})
    query = Q()
    if src.startswith('*'):
        query &= Q(**{'{}__icontains'.format(attr) : parts[0]})
    else:
        query &= Q(**{'{}__istartswith'.format(attr) : parts[0]})
    if src.endswith('*'):
        query &= Q(**{'{}__icontains'.format(attr) : parts[-1]})
    else:
        query &= Q(**{'{}__iendswith'.format(attr) : parts[-1]})
    for p in parts[1:-1]:
        query &= Q(**{'{}__icontains'.format(attr) : p})
    return query
    
def get_game_expand_parameters(expand_str):
    """
    Finds the parameters of the expand query string option.
    
    Args: 
        expand_str: the value of the expand option (e.g. 'sales,highscores(10),similars(5)')
                        
    Returns:
        a 2 dimensional tuple containing
            [0]: highscores parameter 0..INT_MAX
            [1]: similars parameter 0..INT_MAX
    """
    if not expand_str:
        return (0, 0)
        
    expand = expand_str.split(',')
    
    # expand=highscores(number) :
    scores = 0
    # expand=similars(number) :
    similars = 0
        
    for e in expand:
        if scores == 0:
            m = re.match(r'^highscores\(((?:\d)+)\)$', e)
            if m:
                scores = int(m.group(1))
                continue
        if similars == 0:
            m = re.match(r'^similars\(((?:\d)+)\)$', e)
            if m:
                similars = int(m.group(1))
    return (scores, similars)
    
def filter_by_tags(games, taglist, tagfilter):
    """
    Given an iterable of games, returns a list of games
    filtered by tags.
    
    If tagfilter is 'all', a game must have all the tags in taglist in order to remain in the list.
    If tagfilter is 'any', a game must have one or more of the tags in taglist in order to remain in the list.
    
    Args:
        games:      iterable of store.Game objects
        taglist:    list of tags to filter by
        tagfilter:  a string, either 'all' or 'any'
    """
    tag_filtered_games = []
    # yes, 3 nested loops, ugh...
    for g in games:
        matches_found = 0
        for pattern in taglist:
            # convert API search pattern to regex pattern:
            # escape all special characters except '*', which sould be replaced by '.*':
            p = '.*'.join([re.escape(x) for x in pattern.split('*')])
            # add beginning and end characters:
            p = '^' + p + '$'
            for t in g.get_tags():
                if re.match(p, t):
                    matches_found += 1
                    break
            if tagfilter == 'any' and matches_found > 0:
                tag_filtered_games.append(g)  
                break
        if tagfilter != 'any' and matches_found == len(taglist):
            tag_filtered_games.append(g)  
    return tag_filtered_games
    
def api_json_response(request, dictionary):
    """
    Takes a dict and returns an HttpResponse, either as JSON or as JSONP.
    """
    jsondata = dumps(dictionary)
    try:
        function_name = request.GET['callback']
    except:
        pass
    else:
        jsondata = ''.join([function_name + '(', jsondata, ')'])
        return HttpResponse(jsondata, content_type='application/javascript')
    
    return HttpResponse(jsondata, content_type='application/json')
    

def api_games_view(request, id='', titles='', developers='', tags=''):
    """
    RESTfull API view for Games.
    
    Args:
        id:             string in the form '/id/id1/id/id2/.../id/idn'
        titles:         string in the form '/title/t1/title/t2/.../title/tn'
        developers:     string in the form '/dev/d1/dev/d2/.../dev/dn'
        tags:           string in the form '/tagged/t1/tagged/t2/.../tagged/tn'
    
    Returns:
        a JSON string, wrapped in a callback function if specified.
        
    The JSON object contains an array of games containing some info:
        - basic game data 
            title, description, developer, price, tags
        - sales [OPTIONAL, using expand=sales]
            sales
                - total_sales, times_bought
        - highscores [OPTIONAL, using expand=highscores(n)]
            highscores_top_n 
                - score, player, time
        - similar_games [OPTIONAL, using expand=similars(m)]
            similar_games
                - title, developer, match
    
    The returned set of games can be limited to (all filters are OPTIONAL):
        - certain game titles
            title/t1/title/t2       --> (title is t1 OR t2)
        - games tagged with certain tags 
            tagged/t1/tagged/t2     --> (tags contain t1 AND t2),   by default or with tagfilter=all
            tagged/t1/tagged/t2     --> (tags contain t1 OR t2),    with tagfilter=any
        - developers with certain names 
            dev/d1/dev/d2           --> (developer is d1 OR d2)
            
    Use the plus sign (+) for spaces in game titles or developer names (spaces are ot allowed in tags).
    Use only lower case letters (the search is case-insensitive).
        
    The results can also be expanded using url query string options:
        expand=highscores(n) (where n is some integer)
        expand=similars(m)   (where m is some integer)
    To expand both sales stats and highscores, use a comma separator:
        expand=highscores(n),similars(m)
        
    The JSON string can be wrapped in a callback function using the 'callback' query string option:
        callback=mycoolcallback
        
    The tag filtering can be changed using the 'tagfilter' query string option:
        tagfilter=any
        tagfilter=all
        
    Example query:
    
        game_api/v1/games/title/adventure+of+save+button?expand=sales,highscores(1)
    
    could return something like
    
    {
        "games": [
            {
                "location" : "https://root/game_api/v1/games/0",
                "price": "0", 
                "description": 
                "blabla", 
                "developer": "dev", 
                "highscores_top_1": [
                    {
                        "time": "2015-02-02 09:39:12.129399+00:00", 
                        "player": "player", 
                        "score": "17"
                    }
                ],  
                "title": "Adventure of Save Button", 
                "tags": ["additional_feature", "survival", "adventure", "boom!"]
            }
        ]
    }
    """
    id_list = []
    title_list = []
    tag_list = []
    dev_list = []
    if id:
        id_list = [int(x) for x in id.split('/id/') if x]
    if titles:
        title_list = [x.replace('+', ' ') for x in titles.split('/title/') if x]
    if tags:
        tag_list = [x for x in tags.split('/tagged/') if x]      
    if developers:
        dev_list = [x.replace('+', ' ') for x in developers.split('/dev/') if x]
           
    subquery0 = Q()
    for i in id_list:
        subquery0 |= Q(pk__exact=i)    
                    
    subquery1 = Q()
    for t in title_list:
        subquery1 |= wildcard_builder(t, 'title')
    
    subquery2 = Q()
    for d in dev_list:
        subquery2 |= wildcard_builder(d, 'developer__username')
    
    query = (subquery0 & subquery1 & subquery2)
    games = Game.objects.filter(query)
    
    scores, similars = get_game_expand_parameters(request.GET.get('expand', ''))
     
    # because tags is a comma separated string, we must handle it separately (outside of the query):
    if tag_list:
        tagfilter = request.GET.get('tagfilter', 'all')   
        games = filter_by_tags(games, tag_list, tagfilter)
    
    result = {'games' : []}
          
    for g in games:
        d = {'location' : 'https://{}/game_api/v1/games/{}'.format(request.get_host(), g.pk)}
        d.update({'title' : g.title, 'description' : g.description})
        d.update({'developer' : g.developer.username, 'price' : str(g.price), 'tags' : g.get_tags()})
        if scores:
            key = 'highscores_top_' + str(scores) 
            d[key] = []
            for s in list(g.highscore_set.all())[:scores]:
                d[key].append({'time' : str(s.date_time), 'player' : s.player.username, 'score' : float(s.score)})
        if similars:
            key = 'similars_top_' + str(similars)   
            d[key] = []
            for s in list(g.get_related_games())[:similars]:
                d[key].append({'location' : 'https://{}/game_api/v1/games/{}'.format(request.get_host(), s[0].pk), 'title' : s[0].title, 'developer' : s[0].developer.username, 'match' : s[1]})
        result['games'].append(d)
    if not result['games']:
        raise Http404('Resource does not exist')  
        
    return api_json_response(request, result)
    
    
def api_help_view(request):
    return render(request, 'store/apihelp.html')

@login_only
@developers_only    
def api_dev_sales_view(request, id='', titles='', startdate='', enddate=''):
    """
    RESTfull API view for Developers. Shows sales of games by this developer.
    Works otherwise similiarly as api_games_view().
    
    Args:
        id:             string in the form '/id/id1/id/id2/.../id/idn'
        titles:         string in the form '/title/t1/title/t2/.../title/tn'
        startdate:      string in the form YYYY-MM-DD
        enddate:        string in the form YYYY-MM-DD
    
    Returns:
        a JSON string, wrapped in a callback function if specified.
    """
    id_list = []
    title_list = []
    if id:
        id_list = [int(x) for x in id.split('/id/') if x]
    if titles:
        title_list = [x.replace('+', ' ') for x in titles.split('/title/') if x]
                   
    subquery0 = Q()
    for i in id_list:
        subquery0 |= Q(game__pk__exact=i)    
                    
    subquery1 = Q()
    for t in title_list:
        subquery1 |= wildcard_builder(t, 'game__title')
        
    query = (Q(payment_confirmed__exact=True) & Q(game__developer__exact=request.user) & subquery0 & subquery1)
    if startdate:
        try:
            # django wants a timezone: ok, use utc, as we want the response to 
            # not depend on what timezone the requester is in
            d1 = datetime.datetime.strptime(startdate, '%Y-%m-%d').replace(tzinfo=timez.utc)
            query &= Q(date_time__gte=d1)
        except:
            return HttpResponse('Invalid date syntax for startdate, use YYYY-MM-DD.', 
                                content_type='text/plain', status=400) # bad request
    if enddate:
        try:
            d2 = datetime.datetime.strptime(enddate, '%Y-%m-%d').replace(tzinfo=timez.utc)
            query &= Q(date_time__lte=d2)
        except:
            return HttpResponse('Invalid date syntax for enddate, use YYYY-MM-DD.', 
                                content_type='text/plain', status=400) # bad request
    purchases = list(Purchase.objects.filter(query))
        
    result = {'total_sales' : 0, 'total_purchases' : len(purchases), 'detailed_stats' : []}
    detailed_stats = {}
    for p in purchases:
        game = p.game
        gamekey = 'https://{}/game_api/v1/games/{}'.format(request.get_host(), game.pk)
        purchase = {'payment' : float(p.fee), 'time' : str(p.date_time)}
        result['total_sales'] += float(p.fee)
        try:
            detailed_stats[gamekey]['total_sales'] += float(p.fee)
            detailed_stats[gamekey]['total_purchases'] += 1
            detailed_stats[gamekey]['purchases'].append(purchase)
        except KeyError:
            detailed_stats[gamekey] = {'total_sales' : float(p.fee), 'total_purchases' : 1, 'purchases' : [purchase]}
    
    for k, v in detailed_stats.items():               
        result['detailed_stats'].append({'game' : k, 'total_purchases' : v['total_purchases'], 'total_sales' : v['total_sales'], 'purchases' : v['purchases']})
    if not result['detailed_stats']:
        raise Http404('Resource does not exist.')
    
    return api_json_response(request, result)