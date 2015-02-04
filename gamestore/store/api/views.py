from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.db.models import Q
from json import dumps
import re
from django.db.models import Count, Min, Sum, Avg

from store.models import Game


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
    
def get_expand_parameters(expand_str):
    """
    Finds the parameters of the expand query string option.
    
    Args: 
        expand_str: the value of the expand option (e.g. 'sales,highscores(10),similars(5)')
                        
    Returns:
        a 3 dimensional tuple containing
            [0]: sales parameter (True/False)
            [1]: highscores parameter 0..INT_MAX
            [2]: similars parameter 0..INT_MAX
    """
    expand = expand_str.split(',')
    
    # expand=sales :
    sales = False
    # expand=highscores(number) :
    scores = 0
    # expand=similars(number) :
    similars = 0
        
    for e in expand:
        if e == 'sales':
            sales = True
            continue
        if scores == 0:
            m = re.match(r'^highscores\(((?:\d)+)\)$', e)
            if m:
                scores = int(m.group(1))
                continue
        if similars == 0:
            m = re.match(r'^similars\(((?:\d)+)\)$', e)
            if m:
                similars = int(m.group(1))
    return (sales, scores, similars)
    
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
    

def api_view(request, titles='', developers='', tags=''):
    """
    RESTfull API view.
    
    Args:
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
        expand=sales
        expand=highscores(n) (where n is some integer)
        expand=similars(m)   (where m is some integer)
    To expand both sales stats and highscores, use a comma separator:
        expand=sales,highscores(n),similars(m)
        
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
                "price": "0", 
                "description": 
                "blabla", 
                "url": "https://url.com", 
                "developer": "dev", 
                "highscores_top_1": [
                    {
                        "time": "2015-02-02 09:39:12.129399+00:00", 
                        "player": "player", 
                        "score": "17"
                    }
                ], 
                "sales": 
                {
                    "times_bought": 0, 
                    "total_sales": "None"
                }, 
                "title": "Adventure of Save Button", 
                "tags": ["additional_feature", "survival", "adventure", "boom!"]
            }
        ]
    }
    """
    
    title_list = [x.replace('+', ' ') for x in titles.split('/title/') if x]
    tag_list = [x for x in tags.split('/tagged/') if x]      
    dev_list = [x.replace('+', ' ') for x in developers.split('/dev/') if x]
                    
    subquery1 = Q()
    for t in title_list:
        subquery1 |= wildcard_builder(t, 'title')
    
    subquery2 = Q()
    for d in dev_list:
        subquery2 |= wildcard_builder(d, 'developer__username')
    
    query = (subquery1 & subquery2)
    games = Game.objects.filter(query)
    
    sales, scores, similars = get_expand_parameters(request.GET.get('expand', ''))
    if sales:
        games = games.annotate(Sum('purchase__fee')).annotate(Count('purchase'))
     
    # because tags is a comma separated string, we must handle it separately (outside of the query):
    if tag_list:
        tagfilter = request.GET.get('tagfilter', 'all')   
        games = filter_by_tags(games, tag_list, tagfilter)
    
    result = {'games' : []}
          
    for g in games:
        d = {'title' : g.title, 'description' : g.description, 'developer' : g.developer.username, 'price' : str(g.price), 'tags' : g.get_tags()}
        if sales:
            d['sales'] = {'total_sales' : str(g.purchase__fee__sum), 'times_bought' : g.purchase__count}
        if scores:
            key = 'highscores_top_' + str(scores) 
            d[key] = []
            for s in list(g.highscore_set.all())[:scores]:
                d[key].append({'time' : str(s.date_time), 'player' : s.player.username, 'score' : float(s.score)})
        if similars:
            key = 'similars_top_' + str(similars)   
            d[key] = []
            for s in list(g.get_related_games())[:similars]:
                d[key].append({'title' : s[0].title, 'developer' : s[0].developer.username, 'match' : s[1]})
        result['games'].append(d)        
        
    jsondata = dumps(result)
    try:
        function_name = request.GET['callback']
    except:
        pass
    else:
        jsondata = ''.join([function_name + '(', jsondata, ')'])

    
    return HttpResponse(jsondata, content_type='application/json')